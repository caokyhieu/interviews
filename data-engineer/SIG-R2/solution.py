# 1. Two Sum
# Hash Map
# easy
# Return indices of the two numbers that add up to target.

# [2,7,11,15], target=9 → [0,1]

def two_sum(lst, target):
    seen = {} ## create the hash map for storing diff num and its index
    for i,n in enumerate(lst):
        diff = target - n
        if diff in seen:
            return [seen[diff], i]
        seen[n] = i

print("Test case for Two Sum:")
print("Input: [2,7,11,15], target=9, Expected output: [0, 1]")
print(two_sum([2,7,11,15], 9))


# 2. Valid Parentheses
# Stack
# easy
# Given a string of brackets ()[]{}, decide if they're validly matched and nested.

# "([{}])" → True, "(]" → False

def is_valid_parentheses(s):
    stack = []
    mapping = {")": "(", "}": "{", "]": "["} ## hash map for closing and opening brackets
    for char in s:
        if char in mapping: ## if char is closing bracket
            top_element = stack.pop(-1) if stack else None 
            if top_element != mapping[char]:
                return False
        else:
            stack.append(char) ## if char is opening bracket, push to stack
    return not stack ## if stack is empty, return True, else False

print("Test case for Valid Parentheses:")
print("Input: \"([{}])\", Expected output: True")
print(is_valid_parentheses("([{}])"))
print("Input: \"(]\", Expected output: False")
print(is_valid_parentheses("(]"))


# 3. Longest Substring Without Repeating Characters
# Sliding Window
# medium
# Length of the longest substring with all distinct characters.

# "abcabcbb" → 3 ("abc")


def longest_substring_without_repeating_characters(s):
    start = best = 0
    latest = {}
    for i, c in enumerate(s):
        if c in latest and latest[c] >= start:
            start = latest[c] + 1
        latest[c] = i
        best = max(best, i - start +1)
    
    return best

print("Test case for Longest Substring Without Repeating Characters:")
print("Input: \"abcabcbb\", Expected output: 3")
print(longest_substring_without_repeating_characters("abcabcbb"))

# 4. Binary Search
# Searching
# easy
# Return the index of target in a sorted array, else -1. Know it cold — off-by-ones are the classic trap.

# [1,3,5,7,9], target=7 → 3


def binary_search(lst, target):
    left ,right = 0, len(lst) - 1
    while left <= right:
        mid = left + (right - left)//2
        if lst[mid] == target:
            return mid 
        elif lst[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

print("Test case for Binary Search:")
print("Input: [1,3,5,7,9], target=7, Expected output: 3")
print(binary_search([1,3,5,7,9], 7))
        