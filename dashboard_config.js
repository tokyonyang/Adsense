// AdSense SEO Dashboard v1.4 Supabase config
// 브라우저에서는 절대 service_role key를 넣지 마세요.
// 반드시 Supabase의 anon public key만 입력하세요.

window.DASHBOARD_CONFIG = {
  ENABLE_SUPABASE: true,

  // Supabase Project URL
  SUPABASE_URL: "https://oifusdkiqwzbjmlzktar.supabase.co",

  // Supabase Project Settings > API > anon public key
  // 예: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  SUPABASE_ANON_KEY: "PASTE_SUPABASE_ANON_PUBLIC_KEY_HERE",

  // 60초마다 자동 새로고침. 원하지 않으면 0으로 변경.
  REFRESH_SECONDS: 60
};
