# Multi-User Session Test Plan

## Test Scenarios

### 1. Authentication Flow Tests
- **Test 1.1**: New user visits `/` → redirected to `/auth` → completes OAuth → redirected to `/`
- **Test 1.2**: User with expired session visits `/` → redirected to `/auth`
- **Test 1.3**: User visits `/auth` directly → completes OAuth → redirected to `/`
- **Test 1.4**: Authentication failure handling → session cleared → error message

### 2. Session Management Tests
- **Test 2.1**: Session persists across page refreshes
- **Test 2.2**: Session expires after browser closure (session cookies)
- **Test 2.3**: Multiple users in different browsers have isolated sessions
- **Test 2.4**: User can re-authenticate after session expiry

### 3. Multi-User Isolation Tests
- **Test 3.1**: User A's tasks not visible to User B
- **Test 3.2**: User A's task updates don't affect User B's view
- **Test 3.3**: Concurrent task operations by different users
- **Test 3.4**: Each user sees their own summary statistics

### 4. Route Protection Tests
- **Test 4.1**: `/` requires authentication
- **Test 4.2**: `/update` requires authentication
- **Test 4.3**: `/reload` requires authentication
- **Test 4.4**: `/auth` accessible without authentication

### 5. Credential Refresh Tests
- **Test 5.1**: Expired credentials automatically refresh
- **Test 5.2**: Invalid refresh token triggers re-authentication
- **Test 5.3**: Network errors during credential refresh

### 6. Data Consistency Tests
- **Test 6.1**: Task updates persist in session
- **Test 6.2**: Reload functionality updates session tasks
- **Test 6.3**: Filter operations work with session data
- **Test 6.4**: Task hierarchy (parent/child) maintained per user

## Automated Test Implementation

### Unit Tests (test_app.py)
1. Test `require_auth` decorator
2. Test session credential conversion functions
3. Test route responses with/without authentication
4. Test error handling in auth flow

### Integration Tests
1. Test complete authentication flow
2. Test multi-user task isolation
3. Test session persistence
4. Test credential refresh scenarios

## Manual Testing Checklist

### Setup
- [ ] Start application with `python app.py`
- [ ] Open multiple browser windows (different users)
- [ ] Ensure `credentials.json` exists

### Test Execution
- [ ] Test 1: New user authentication flow
- [ ] Test 2: Multiple users simultaneously
- [ ] Test 3: Session expiry handling
- [ ] Test 4: Task operations per user
- [ ] Test 5: Reload functionality
- [ ] Test 6: Error scenarios

### Expected Outcomes
- Each user maintains isolated task lists
- Authentication redirects work correctly
- No cross-user data leakage
- Session management functions properly
- All routes protected appropriately