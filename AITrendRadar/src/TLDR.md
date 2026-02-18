# TL;DR - Just Tell Me What to Run

**No explanations. Just commands.**

---

## 🚀 After Downloading

Open terminal in the project folder, then:

```bash
# Step 1: Fix imports (once)
npm run fix-imports

# Step 2: Install
npm install

# Step 3: Run
npm run dev
```

Open browser: **http://localhost:5173**

---

## ✅ That's It

If it works: **You're done!** 🎉

If not: See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

## 🔄 Every Other Day

Just run:

```bash
npm run dev
```

---

## Common Fixes

**Error: "Cannot find module"**
```bash
npm run fix-imports
npm install
npm run dev
```

**Error: "Port in use"**
```bash
npm run dev -- --port 3000
```

**Error: "npm: command not found"**
- Install Node.js: https://nodejs.org/

---

## Stop Server

Press `Ctrl + C` in terminal

---

**Need details?** See [FRESH_INSTALL_GUIDE.md](./FRESH_INSTALL_GUIDE.md)