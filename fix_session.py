#!/usr/bin/env python
"""
Script to fix session persistence in signup flow
"""

# Read the views.py file
with open('listings/views.py', 'r') as f:
    lines = f.readlines()

# Find the line with "Sign-up successful! OTP sent"
modified = False
for i, line in enumerate(lines):
    # Look for the line that sets signup_email in session
    if "request.session['signup_email'] = user.email" in line and not modified:
        # Check if the next line is the redirect
        if i + 1 < len(lines) and "return redirect('listings:verify_signup_email')" in lines[i + 1]:
            # Add session.create() call between them
            indent = len(line) - len(line.lstrip())
            lines.insert(i + 1, " " * indent + "request.session.create()  # Force session creation\n")
            modified = True
            break

# Also fix signin and other OTP paths
for i, line in enumerate(lines):
    if "request.session['signin_user_id']" in line and i + 1 < len(lines):
        if "request.session['signin_otp_email']" in lines[i + 1] and i + 2 < len(lines):
            if "return redirect('listings:signin_otp_verify')" in lines[i + 2]:
                indent = len(line) - len(line.lstrip())
                lines.insert(i + 2, " " * indent + "request.session.create()  # Force session creation\n")
                break

if modified:
    # Write back
    with open('listings/views.py', 'w') as f:
        f.writelines(lines)
    print('✓ Fixed session persistence in views.py')
else:
    print('⚠ Could not find session lines to fix')
