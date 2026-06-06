# NasPortal Dashboard Design Brief

## Source Of Truth

The implementation should follow these reference images:

- [Design-Light.png](D:/projects/NasPortal/docs/Design-Light.png)
- [Design-Dark.png](D:/projects/NasPortal/docs/Design-Dark.png)

When the code and the screenshots disagree, the screenshots win.

## Product Shape

NasPortal is a personal terminal portal for launching apps, running lightweight terminal actions, and quickly reaching admin and VPS-related status from one local-first dashboard.

This is not a generic link page and not a heavy SPA. It should feel like a polished command-center home screen.

## Technical Direction

- Backend: FastAPI + SQLAlchemy + Jinja2 SSR
- Frontend: plain CSS + vanilla JavaScript ES modules
- No React / Vue / Next
- No heavy component library
- No frontend router

## Layout

### Left Sidebar

- Brand block: `NasPortal` + `personal terminal`
- Navigation:
  - Dashboard
  - Terminal
  - Apps
- User identity card
- User identity is pinned near the lower-left corner

### Top Bar

- Command-style global search input
- Lightweight app search
- `+` manage-link action

### Main Dashboard

- Hero panel with title, supporting copy, command line, action buttons, and quick links
- Metric cards:
  - CPU Load
  - Memory
  - Storage
  - Latency
- Monitor summary card
- Apps section with `Icons / Cards` toggle
- Terminal command panel, opened from sidebar

## Data Mapping

The homepage continues to use the existing `websites` data source.

- `title` -> app or resource name
- `description` -> secondary copy
- `url` -> launch target
- `is_public` -> public/private chip
- owner username -> owner chip when available

No database schema change is required for the first version.

## Interaction Rules

- The search input filters app tiles on the client.
- `Icons / Cards` only changes presentation density.
- `Open app launcher` scrolls to the Apps section.
- `+` opens `/admin`.
- View mode should persist in `localStorage`.
- `/` or `Ctrl+K` focuses the command search field.
- Terminal supports `help`, `apps`, `open <name>`, `admin`, and `logout`.

## Visual Direction

### Light Theme

- Soft paper-like background
- Blue primary action color
- Green status accents
- High readability
- Pixel-terminal display styling for titles

### Dark Theme

- Deep navy background
- Blue and green neon-like accents
- The same layout and spacing as light mode
- No glow-heavy cyberpunk excess

## Runtime And Verification

- `.env` must include `ENV=DEV|PRD`
- `launch.bat` is the standard local entry point
- `DEV` uses hot reload for implementation work
- `PRD` uses the production startup path, with a Windows-safe fallback for local execution

After implementation:

1. Start the app through `launch.bat`
2. Open the local page in the Codex in-app browser
3. Compare the real page to `Design-Light.png`
4. Fix layout or styling mismatches
5. Repeat until the visual result is acceptably close

## First-Version Boundaries

- VPS metrics are served by `/api/vps/status` and refreshed by the frontend
- The admin page is not redesigned in this phase
- `/api/vps/status` provides live CPU, memory, storage, latency, and monitor summary data
- No schema migration is needed
- Light theme is the primary implementation target
