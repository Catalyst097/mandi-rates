export default {
  // Triggered by Cloudflare Cron Triggers at exact scheduled times
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
        console.log(`[SUCCESS] Successfully dispatched GitHub Actions workflow ${workflow} for ${owner}/${repo}`);
      } else {
        const errorText = await response.text();
        console.error(`[ERROR] Failed to dispatch workflow. Status: ${response.status}. Body: ${errorText}`);
      }
    } catch (err) {
      console.error(`[EXCEPTION] Network or fetch error: ${err.message}`);
    }
  },

  // Supports manual HTTP GET /trigger for 1-tap mobile trigger or browser testing!
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === '/trigger') {
      const owner = env.GH_OWNER || 'systemiclogics-beep';
      const repo = env.GH_REPO || 'mandi-rates';
      const workflow = env.GH_WORKFLOW || 'daily_mandi_sync.yml';

      const response = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflow}/dispatches`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${env.GH_PAT}`,
            'User-Agent': 'bharatmandi-cron-trigger',
            'Accept': 'application/vnd.github+json',
          },
          body: JSON.stringify({ ref: 'main' }),
        }
      );

      if (response.status === 204) {
        return new Response(JSON.stringify({ success: true, message: 'GitHub Actions triggered successfully!' }), {
          headers: { 'Content-Type': 'application/json' },
        });
      } else {
        const text = await response.text();
        return new Response(JSON.stringify({ success: false, status: response.status, error: text }), {
          status: response.status,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    }

    return new Response('BharatMandi Cron Trigger Worker is active. Send GET /trigger to dispatch manually.', {
      headers: { 'Content-Type': 'text/plain' },
    });
  }
};
