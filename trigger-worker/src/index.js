export default {
  // Triggered by Cloudflare Cron Triggers at exact scheduled times (11:15 AM, 2:05 PM, 3:45 PM IST)
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

  // Manual HTTP Trigger (Protected with mandatory Secret Key)
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Only respond to /trigger endpoint
    if (url.pathname === '/trigger') {
      // 1. Verify Secret Key (Header, Bearer token, or ?key= param)
      const expectedSecret = env.TRIGGER_SECRET;
      const headerKey = request.headers.get('x-trigger-key');
      const authHeader = request.headers.get('authorization');
      const bearerKey = authHeader && authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;
      const queryKey = url.searchParams.get('key');

      const providedKey = headerKey || bearerKey || queryKey;

      if (!expectedSecret || providedKey !== expectedSecret) {
        return new Response(JSON.stringify({ 
          success: false, 
          error: 'Unauthorized: Valid secret key required to dispatch workflows.' 
        }), {
          status: 401,
          headers: { 'Content-Type': 'application/json' },
        });
      }

      // 2. Dispatch to GitHub Actions
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
        return new Response(JSON.stringify({ 
          success: true, 
          message: `GitHub Actions ${workflow} dispatched successfully for ${owner}/${repo}` 
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      } else {
        const text = await response.text();
        return new Response(JSON.stringify({ 
          success: false, 
          status: response.status, 
          error: text 
        }), {
          status: response.status,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    }

    // Default response: Generic 404 (Does not leak the trigger path)
    return new Response('Not Found', { status: 404 });
  }
};
