# Implementing an MCP server (2026-07-28 spec) and Agent Skills

> Concepts: [../05-protocols-mcp-a2a-skills.md](../05-protocols-mcp-a2a-skills.md). Code: [../code/mcp_server/notes_server.py](../code/mcp_server/notes_server.py). Test: `test_mcp_server_roundtrip` in [../code/tests/test_other.py](../code/tests/test_other.py).
>
> Verified against **MCP Python SDK 2.2.0**, which negotiates protocol **2026-07-28** (the test asserts it).

---

## 1. SDK 2.x essentials (things that changed from 1.x tutorials)

| 1.x tutorials | 2.x (current) |
|---|---|
| `from mcp.server.fastmcp import FastMCP` | `from mcp.server import MCPServer` (FastMCP was renamed; importing the old path fails with a migration hint) |
| `ctx.elicit(...)` in the tool body, held-open stream | a **resolver** returning `Elicit(message, Schema)`, injected via `Annotated[T, Resolve(fn)]`: the SDK sends `input_required` (MRTR) to 2026-07-28 clients and falls back to classic elicitation for older ones |
| session state in server memory | stateless: each request self-describing; keep state in your DB |
| no list caching | `MCPServer(cache_hints={"tools/list": CacheHint(ttl_ms=..., scope="public")})` |
| any exception → error text to the model | only `ToolError` messages reach the model; other exceptions become a generic "Error executing tool X" |

---

## 2. Walkthrough of `notes_server.py`

```python
mcp = MCPServer("notes", instructions="...",
                cache_hints={"tools/list": CacheHint(ttl_ms=3_600_000, scope="public")})

@mcp.tool()
def search_notes(query: str, tag: str | None = None,
                 limit: Annotated[int, Field(ge=1, le=50)] = 10, offset: Annotated[int, Field(ge=0)] = 0,
                 response_format: Literal["concise", "detailed"] = "concise") -> SearchResult:
    """Search notes ... Use this before create_note ... Results are paginated: use next_offset."""
```
- **Type hints are the schema; the docstring is the description.** Write the docstring for the model: when to use the tool, what it returns, how to page.
- Returning a Pydantic model gives **structured output** (`structured_content` on the client) plus a text rendering.
- `Field(ge=1, le=50)` bounds are validated by the SDK before your code runs.

**Confirmation with MRTR:**
```python
class Confirm(BaseModel):
    confirm: bool

def ask_delete_confirmation(note_id: int) -> Elicit[Confirm]:
    return Elicit(f"Permanently delete note {note_id}?", Confirm)

@mcp.tool()
def delete_note(note_id: int, confirmation: Annotated[Confirm, Resolve(ask_delete_confirmation)]) -> str:
    if not confirmation.confirm: return "Not deleted: ..."
```
The resolver receives tool arguments by name. On a 2026-07-28 client the first `tools/call` returns `input_required`; the client asks the user and **retries the same call** with the answers, and the SDK re-runs the resolver and injects the result. No stream is held open, so this works behind any load balancer. If the user declines or cancels, the call is aborted (annotate with `ElicitationResult[Confirm]` instead to branch on decline yourself).

**Expected errors:**
```python
raise ToolError(f"No note with id {note_id}. Use search_notes to find valid ids.")
```

**Run it:**
```bash
cd code
.venv/bin/python -m mcp_server.notes_server            # stdio
.venv/bin/python -m mcp_server.notes_server --http     # streamable HTTP on 127.0.0.1:8000
# use from Claude Code: absolute paths, since the client picks the working directory
claude mcp add notes -e NOTES_DB=/abs/path/notes.db -- /abs/path/code/.venv/bin/python /abs/path/code/mcp_server/notes_server.py
```

**Test it in-process** (no network, no subprocess):
```python
async with Client(srv.mcp, elicitation_callback=on_elicit) as c:
    assert c.protocol_version == "2026-07-28"
    await c.call_tool("create_note", {...})
```

---

## 3. Designing the tool set

1. **Start from user tasks, not API endpoints.** "Find and summarise notes about X" → `search_notes` + `read_note`, not `list_notes` + `get_note_body` + `get_note_tags`.
2. **Search before create** in the instructions and descriptions prevents duplicates.
3. **Paginate** with `next_offset`, and say in the description that results are paginated.
4. **Concise by default**, with a `response_format` switch for detail.
5. **IDs flow between tools.** Say where valid ids come from ("ids come from search_notes").
6. **Dangerous operations confirm** via elicitation, and are annotated (`@mcp.tool(annotations=ToolAnnotations(destructive_hint=True))`, which is sent as `destructiveHint` on the wire) so clients can apply policy.
7. **Keep the count small** (roughly under 15–20 per server). Many servers × many tools overwhelms the model's context. Clients increasingly use tool search / deferred loading, but fewer, better tools still win.

---

## 4. Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: mcp.server.fastmcp` | SDK 2.x | `from mcp.server import MCPServer` (or pin `mcp<2` for old code) |
| Model sees "Error executing tool X" with no detail | raised a plain exception | raise `ToolError("what went wrong + what to do next")` |
| stdio server hangs or clients see garbage | `print()` to stdout: stdout **is** the protocol channel on stdio | log to stderr (`logging`), never print |
| Works locally, fails behind a load balancer | per-session state in process memory | stateless handlers; state in DB/cache keyed by user/resource |
| Model calls the wrong tool / invents params | vague docstrings, overlapping tools | rewrite descriptions ("use X for…, not for…"), merge overlapping tools, enums for fixed choices |
| Huge responses blow the model's context | returning whole tables/files | pagination + snippets + `response_format` |
| Clients re-fetch `tools/list` constantly | no cache hints | `cache_hints` on the server (or `ttl_ms` in the result) |
| Elicitation never reaches the user | client lacks elicitation capability | handle `ElicitationResult` decline/cancel; document the requirement |
| Auth breaks after upgrading | Dynamic Client Registration deprecated; issuer validation now required | CIMD (client ID = metadata document URL); validate issuer (RFC 9207) |
| A tool description changed and the agent behaves oddly | "rug pull" risk: descriptions are prompt text | pin server versions; review description diffs like code |

---

## 5. Agent Skills (SKILL.md), step by step

```
skills/release-notes/
├── SKILL.md
├── template.md
└── collect_changes.py
```

```markdown
---
name: release-notes
description: Write release notes from merged PRs in our house style. Use when the user asks for release notes, a changelog, or "what shipped" for a version or date range.
---

# Writing release notes

1. Run `python collect_changes.py --since <tag>` to list merged PRs with labels.
2. Group by label: Features, Fixes, Breaking changes (always first if any).
3. Use `template.md`. One line per change, user-facing language, link the PR.
4. Breaking changes need a migration sentence.
```

**What makes a skill work:**
| Part | Advice |
|---|---|
| `description` | the only part that's always in context, so it decides whether the skill triggers. Say **what** it does and **when** to use it, with trigger phrases users actually say |
| body | concrete steps, file names, commands; examples of good output; what *not* to do |
| extra files | long references and templates load only when needed (progressive disclosure) |
| scripts | deterministic work (parsing, validation) belongs in code, not in prose instructions |

**Common errors:** the skill never triggers (description too vague, or phrased differently from real requests) · triggers on unrelated tasks (description too broad) · the body is too long, so it should be split into referenced files · scripts assume a working directory or dependencies the agent doesn't have.

**Test a skill** by writing 10 prompts that *should* trigger it and 10 that shouldn't, and checking which ones load it. Then check output quality on the triggering ones.

---

## 6. Exercises
1. Run `pytest tests/test_other.py -k mcp -v`; then run the server over HTTP and connect with the MCP Inspector (`npx @modelcontextprotocol/inspector`).
2. Add an `update_note` tool that uses MRTR to confirm only when the body shrinks by more than 50%.
3. Put the server behind two processes (different ports) with a round-robin proxy and show that the delete confirmation still works (stateless).
4. Write a `notes-weekly-review` skill that uses the MCP tools to produce a weekly summary. Measure how reliably it triggers.
