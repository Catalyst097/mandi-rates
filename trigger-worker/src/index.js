export default {
  // Automated Cloudflare Cron: Fires internally at 11:15 AM, 2:05 PM, 3:45 PM IST
  async scheduled(controller, env, ctx) {
    const owner = env.GH_OWNER || 'systemiclogics-beep';
    const repo = env.GH_REPO || 'mandi-rates';
    const workflow = env.GH_WORKFLOW || 'daily_mandi_sync.yml';

    const url = `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflow}/dispatches`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.GH_PAT}`,
          'User-Agent': 'bharatmandi-cron-trigger',
          'Accept': 'application/vnd.github+json',
        },
        body: JSON.stringify({ ref: 'main' }),
      });

      if (response.status === 204) {
        console.log(`[SUCCESS] Cron successfully dispatched ${workflow} for ${owner}/${repo}`);
      } else {
        const errorText = await response.text();
        console.error(`[ERROR] Failed to dispatch workflow. Status: ${response.status}. Body: ${errorText}`);
      }
    } catch (err) {
      console.error(`[EXCEPTION] Network error during cron dispatch: ${err.message}`);
    }
  },

  // Reject all external HTTP web requests with 404 (Pure private cron worker, 0% public attack surface)
  async fetch() {
    return new Response('Not Found', { status: 404 });
  }
};
