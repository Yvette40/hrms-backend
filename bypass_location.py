# Quick fix - make location optional
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the location verification
old_code = '''        # Verify location
        is_valid, distance, location_msg = verify_location(user_latitude, user_longitude)
        if not is_valid:
            return jsonify({
                'error': '🚫 Location verification failed',
                'message': location_msg,
                'distance': distance
            }), 403'''

new_code = '''        # Verify location (OPTIONAL FOR TESTING)
        if user_latitude and user_longitude:
            is_valid, distance, location_msg = verify_location(user_latitude, user_longitude)
            if not is_valid:
                print(f"⚠️  Location check failed: {location_msg}")
                # For testing, just warn but allow check-in
        
        # Allow check-in regardless of location for testing
        distance = 0
        location_msg = "Location check bypassed for testing"'''

content = content.replace(old_code, new_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Location check made optional!')
print('Restart Flask and try check-in again.')
