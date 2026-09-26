# BharatMandi Cloudflare Cron Trigger Worker

Automatically dispatches the GitHub Actions `daily_mandi_sync.yml` workflow via GitHub's REST API at exact scheduled times to completely bypass GitHub Actions cron scheduler delays.

## Cost: ₹0.00 Forever
- Uses 3 Cron Triggers (out of 5 allowed on Free plan).
- Uses ~3 requests per day (out of 100,000 allowed per day on Free plan).

## Schedule (IST):
1. `45 5 * * *` -> 11:15 AM IST (Morning mandi arrivals)
2. `35 8 * * *` -> 02:05 PM IST (Midday updates)
3. `15 10 * * *` -> 03:45 PM IST (Afternoon auction closing)

## Deployment Options

### Option 1: Via Cloudflare Dashboard (Easiest - 60 seconds)
1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) -> **Workers & Pages** -> **Create application** -> **Create Worker**.
2. Name it `mandi-trigger` and click **Deploy**.
3. Click **Edit code**, copy and paste the contents of `src/index.js`, and click **Deploy**.
4. Go to **Settings** -> **Variables and Secrets**:
   - Add Secret: `GH_PAT` = your GitHub Personal Access Token (classic token with `repo` scope, or fine-grained token with `Actions: write`).
   - Add Secret: `TRIGGER_SECRET` = your chosen secret password/passphrase (to protect the manual `/trigger` endpoint from public abuse).
5. Go to **Settings** -> **Triggers** -> **Cron Triggers**:
   - Add Trigger: `45 5 * * *`
   - Add Trigger: `35 8 * * *`
   - Add Trigger: `15 10 * * *`

### Option 2: Via Wrangler CLI
```bash
cd trigger-worker
npx wrangler secret put GH_PAT
npx wrangler secret put TRIGGER_SECRET
npx wrangler deploy
```

## Authenticated Manual Trigger (Protected)
To prevent unauthorized users from draining your GitHub Action quotas, manual dispatch strictly requires your `TRIGGER_SECRET`:
- **In browser**: `https://mandi-trigger.<your-subdomain>.workers.dev/trigger?key=YOUR_TRIGGER_SECRET`
- **Via cURL / Header**:
  ```bash
  curl -X POST "https://mandi-trigger.<your-subdomain>.workers.dev/trigger" \
       -H "X-Trigger-Key: YOUR_TRIGGER_SECRET"
  ```
Unauthenticated requests will receive `401 Unauthorized`, and unmapped routes return `404 Not Found`.
