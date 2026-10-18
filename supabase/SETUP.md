# Turning on accounts (Supabase)

Without this, CalcGame still works: progress stays in each student's browser and the account features are hidden.

Privacy design: students make up a username and password. No real names, emails or student IDs are collected. The tool is optional and ungraded; completion codes let you give credit inside Canvas without the app knowing who anyone is.

## 1. Create the project (about 5 minutes)
1. Go to supabase.com, sign in, and click **New project**. Name it `calcgame`, choose the **Free** plan, pick a US West region, and save the database password somewhere safe.
2. Wait for it to finish setting up.

## 2. Turn off email confirmation
**Authentication → Sign In / Providers → Email**: turn **Confirm email** OFF and save. (Accounts use made-up addresses built from the username, so no email can ever be confirmed or sent.)

## 3. Create the tables
**SQL Editor → New query**, paste the whole of `supabase/schema.sql`, press **Run**. It is safe to run again after updates.

## 4. Connect the app
**Project Settings → API** (or **API Keys**): copy the **Project URL** and the **anon / publishable** key into `js/config.js`:

```js
supabaseUrl:'https://xxxx.supabase.co',
supabaseKey:'eyJ...or sb_publishable_...',
```

The anon key is meant to be public; the database rules (row level security) decide what each account can see. **Never** put the `service_role` / secret key in the site.

## 5. Your instructor account
1. Open `instructor.html` on the site (for example `https://dallascarl.github.io/CalcGame/instructor.html`).
2. Open **First time? Create the instructor account**, pick a username and a password of 8+ characters.
3. The page shows one line of SQL. Run it in the SQL Editor. Then press **check again**.
4. On the **Classes** tab, create a class. Give students the class code.

## Day to day
- **Forgot password:** Students tab → Reset password, then tell the student in person.
- **Completion codes:** students paste codes into a Canvas quiz; drop the quiz's Student Analysis CSV on the Completion codes tab, then Mark as used.
- **Free plan pause:** Supabase pauses free projects after about a week with no activity. If students report the app can't reach the server after a break, open the Supabase dashboard and press **Restore**.

## Trying it without a server
Add `?mock=1` to either page (`index.html?mock=1`, `instructor.html?mock=1`). Everything is stored in that browser only. The demo class code is `DEMO1`.
