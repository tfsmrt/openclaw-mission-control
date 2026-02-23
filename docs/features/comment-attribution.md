# Comment Attribution

## Overview

Task comments and board chat messages are attributed to the correct author — human users show their real name; agents show their agent name.

## How It Works

### Task Comments

When a user posts a task comment, two fields are stored on `ActivityEvent`:

| Field | Type | Purpose |
|---|---|---|
| `created_by_user_id` | UUID (FK → users) | Immutable user reference for audit trail |
| `author_name` | string (denormalized) | Display name captured at write time |

`author_name` is written from `user.name` at comment creation time. Denormalization means display stays correct even if the user later changes their profile name.

### Board Chat Messages

When a user sends a board chat message, the `source` field is derived **server-side** from the authenticated actor — the client-provided `source` value is **ignored for chat messages**. This prevents display-name spoofing.

- Human user → `user.name`
- Agent → `agent.name`

### Display (Frontend)

Old fallback (`currentUserDisplayName`) replaced with `comment.author_name ?? "User"` so every comment shows the actual author regardless of who is viewing.

## Migration

Migration `c1a2b3d4e5f6` adds `created_by_user_id` and `author_name` to `activity_events`.

```bash
# Applied automatically on backend startup
alembic upgrade head
```

## Troubleshooting

**Comments showing the wrong name:**
- Check `users.name` and `users.preferred_name` for the user in question.
- `preferred_name` is a user-settable nickname (set via board onboarding). It does **not** affect comment attribution — only `name` is used for chat and comment `author_name`.
- To clear a misconfigured `preferred_name`:
  ```sql
  UPDATE users SET preferred_name = NULL WHERE email = 'user@example.com';
  ```
- Existing `board_memory` rows with wrong `source` can be corrected directly:
  ```sql
  UPDATE board_memory SET source = 'CorrectName' WHERE source = 'WrongName' AND board_id = '<board_id>';
  ```
