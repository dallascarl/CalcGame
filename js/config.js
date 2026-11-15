/* Server settings. OFF for Spring 2027: student data may not be stored on servers UVU does not own, so
   progress stays in each browser and students hand in app codes (js/appcode.js) instead.
   Leave supabaseUrl empty to run with no server (progress stays in each browser).
   Fill these in from Supabase: Project Settings → API. The anon/publishable key is safe to publish.
   NEVER put the service_role key here. */
window.CALCGAME_CONFIG={
  supabaseUrl:'',
  supabaseKey:'',
  /* accounts are username-only; this made-up domain turns a username into the login Supabase expects */
  userDomain:'users.calcgame.app'
};
