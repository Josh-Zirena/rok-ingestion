# RoK Leaderboard Frontend

Frontend application for the RoK player leaderboard, built with Vite and vanilla JavaScript.

## Setup

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Configure API endpoint:**

   Update the `VITE_API_URL` in `.env.development` to point to your API:
   
   - For local testing: `http://localhost:3001`
   - For deployed API: Use your API Gateway URL from `terraform output leaderboard_api_url`

## Development

Start the development server:

```bash
npm run dev
```

This will open the app at `http://localhost:3000` with hot module replacement.

## Building for Production

Build optimized static files:

```bash
npm run build
```

Output will be in the `dist/` directory, ready to deploy to S3.

## Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── index.html              # Main HTML file
├── src/
│   ├── main.js            # App entry point
│   ├── style.css          # Global styles
│   ├── api/
│   │   └── leaderboard.js # API client
│   └── components/
│       └── LeaderboardTable.js  # Table rendering
├── .env.development       # Dev environment config
├── .env.production        # Prod environment config
└── vite.config.js         # Vite configuration
```

## Using the App

1. Enter a kingdom ID (e.g., `1234` or `3951`)
2. Select a metric (Power, Killpoints, Total Kills, Deaths)
3. Choose either "Use Latest" or select a specific date
4. Set the limit (number of players to display)
5. Click "Load Leaderboard"

## API Integration

The app calls two endpoints:

- `GET /health` - Health check (called on page load)
- `GET /leaderboard?kingdom=X&metric=Y&dt=Z&limit=N` - Fetch leaderboard data

Query parameters:
- `kingdom`: Kingdom ID (1-6 digits)
- `metric`: One of `power`, `killpoints`, `kills`, `deads`
- `dt`: Date in `YYYY-MM-DD` format or `latest`
- `limit`: Number of results (1-500)

## Next Steps (Phase 2+)

- Enhanced component architecture
- Better styling with Tailwind or similar
- More interactive features (search, filters, auto-refresh)
- Deploy infrastructure (S3 + CloudFront)
