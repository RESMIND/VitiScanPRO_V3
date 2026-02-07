# 🎨 UI pentru Sistemul de Autorizare VitiScan v3

Acest document oferă o prezentare completă a interfețelor utilizator create pentru feature-urile enterprise de autorizare.

---

## 📄 Pagini Implementate

### 1. 🔐 Beta Onboarding Flow

#### `/beta-request` - Formular Cerere Acces
**Scop:** Permite utilizatorilor să solicite acces la platforma beta

**Features:**
- ✅ Form validation pentru email și telefon
- ✅ Câmpuri opționale: companie, regiune, motiv
- ✅ Design responsive cu Tailwind CSS
- ✅ Success state cu auto-redirect
- ✅ Error handling complet

**Câmpuri:**
- Email Address (required)
- Număr Telefon (required)
- Nume Complet (required)
- Companie / Fermă (optional)
- Regiune (dropdown cu regiuni viticole)
- De ce vrei acces beta? (textarea)

**Flow:**
1. User completează formularul
2. POST → `/beta-requests`
3. Backend salvează în `beta_requests` collection
4. Backend trimite SMS + Email cu `register_token`
5. Success message + redirect

---

#### `/register-complete?token=XYZ` - Finalizare Cont
**Scop:** User finalizează crearea contului cu parola

**Features:**
- ✅ Token verification la încărcare
- ✅ Afișare detalii pre-populate (nume, email)
- ✅ Password validation (min 8 chars)
- ✅ Confirm password matching
- ✅ Visual feedback pentru cerințe parolă
- ✅ Error states pentru token expirat/invalid

**Flow:**
1. User accesează link din SMS/Email
2. GET `/beta-requests/verify/{token}` → verifică valabilitate
3. Afișează form cu nume/email pre-completate
4. User setează parolă
5. POST `/beta-requests/complete/{token}` cu password
6. Redirect → `/login?registered=true`

---

#### `/admin/beta-requests` - Admin Panel
**Scop:** Adminii gestionează cererile de acces beta

**Features:**
- ✅ Tabel complet cu toate cererile
- ✅ Stats dashboard (Total, Pending, Approved, Rejected)
- ✅ Filtrare: All, Pending, Approved, Rejected
- ✅ Status badges cu culori distinctive
- ✅ Acțiuni: Approve / Reject pentru pending requests
- ✅ Timestamp formatat (ro-RO locale)
- ✅ Responsive design

**Coloane Tabel:**
- Utilizator (nume + reason preview)
- Contact (email + telefon)
- Companie / Regiune
- Status (badge cu icon)
- Data (formatted)
- Acțiuni (butoane Aprobă/Refuză)

**API Endpoints folosite:**
- `GET /admin/beta-requests` - listă cereri
- `POST /admin/beta-requests/{id}/approve` - aprobă
- `POST /admin/beta-requests/{id}/reject` - refuză

---

### 2. 📊 Audit Logs & Debugging

#### `/admin/audit/logs` - Audit Trail Dashboard
**Scop:** Adminii văd tot istoricul de autorizare

**Features:**
- ✅ Stats cards: Total Events, Allow %, Deny %, Top User
- ✅ Filtre avansate: User ID, Action, Outcome, Perioada (1-90 zile)
- ✅ Tabel complet cu toate log-urile
- ✅ Mechanism badges (RBAC/ABAC/ReBAC)
- ✅ Outcome badges (Allow/Deny)
- ✅ Buton "Why?" → modal cu detalii complete
- ✅ Timestamp localizat
- ✅ Real-time refresh când schimbi filtre

**Filtre disponibile:**
- User ID (text input)
- Acțiune (dropdown: read/write/delete/share)
- Outcome (dropdown: allow/deny)
- Perioada (dropdown: Azi, 7 zile, 30 zile, 90 zile)

**Coloane Tabel:**
- Timestamp
- User ID
- Acțiune
- Resursă (type:id)
- Mechanism (badge)
- Outcome (badge)
- Detalii (buton Why?)

**Modal "Why?":**
- Timestamp complet
- User ID
- Acțiune
- Resursă (format mono)
- Mechanism badge
- Outcome badge
- JSON complet cu detalii (expandable)

**API Endpoints:**
- `GET /admin/audit/logs?user_id=&action=&outcome=&days=` - logs filtrate
- `GET /admin/audit/stats` - statistici

---

#### `/authz/debug` - Authorization Debugger
**Scop:** QA/Dev pot simula decizii de autorizare fără efecte

**Features:**
- ✅ Scenarii predefinite (4 cazuri comune)
- ✅ Editor JSON pentru request manual
- ✅ Dry Run toggle (ON = nu salvează audit log)
- ✅ Test button cu loading state
- ✅ Response explicat vizual
- ✅ Mechanism badge
- ✅ Matched rules list
- ✅ Decision badge mare (Allow/Deny)
- ✅ Full JSON expandable

**Scenarii Predefinite:**
1. 👤 Admin Full Access (admin → delete parcel)
2. 🔒 MFA Required (user fără MFA → delete)
3. 🌍 Region Restriction (user din Occitanie → parcel PACA)
4. 👁️ Viewer ReBAC (consultant → read parcel)

**Request Builder:**
- Subject JSON (textarea editabil)
- Resource JSON (textarea editabil)
- Action (dropdown: read/write/delete/share)
- Dry Run toggle (switch visual)

**Response Display:**
- Decision badge central (ALLOW/DENY)
- Dry Run indicator
- Mechanism badge (RBAC/ABAC/ReBAC)
- Matched rules (listă cu bullets)
- Explicație text (human-readable)
- Full JSON (details expandable)

**API Endpoint:**
- `POST /authz/why?dry_run=true` - test autorizare

---

### 3. 🔑 Capability Tokens Flow

#### `/parcels/:id/share` - Generare Token
**Scop:** Owner/Admin generează token temporar pentru sharing

**Features:**
- ✅ Form pentru configurare token
- ✅ Valabilitate: 1h, 6h, 24h, 3 zile, 7 zile
- ✅ Max uses (0 = unlimited)
- ✅ Target subject (optional - restrict to specific user)
- ✅ Security info box
- ✅ Token display ONE-TIME după generare
- ✅ Copy to clipboard functionality
- ✅ Token details summary
- ✅ Warning about one-time view
- ✅ Acțiuni: Generate Alt Token / Înapoi la Parcelă

**Form Fields:**
- Valabilitate (dropdown ore/zile)
- Număr maxim utilizări (number input)
- User ID Specific (text input, optional)

**Token Display (Show Once):**
- Success message
- Link complet: `https://.../view/{token}`
- Copy button cu feedback
- Token details (valabilitate, max_uses, target)
- Warning box (nu mai poate fi recuperat)

**API Endpoint:**
- `POST /authz/tokens` - creează token

---

#### `/view/:token` - Vizualizare cu Token
**Scop:** Guest/Consultant accesează resursă cu token temporar

**Features:**
- ✅ Token verification automată
- ✅ Warning banner: Read-Only + expiry countdown
- ✅ Parcel details (nume, suprafață, cultură)
- ✅ Map integration (Leaflet cu coordonate)
- ✅ Read-only badge
- ✅ Info box despre limitări acces
- ✅ Error state pentru token invalid/expirat
- ✅ Loading state la verificare

**Layout:**
- Warning Banner (yellow): Read-Only + timp rămas + uses count
- Header: Nume parcelă + Read-Only badge
- Stats Cards: Suprafață, Cultură, ID Parcelă
- Map: Leaflet integration (non-editable)
- Info Box: Detalii despre acces temporar
- Footer: Powered by VitiScan

**Error States:**
- Token expirat
- Token revocat
- Token invalid
- Resursa nu există

**API Endpoints:**
- `POST /authz/tokens/{token}/verify` - verifică token
- `GET /parcels/{id}` - fetch resource

---

## 🧩 Componente Reutilizabile

### `NavigationMenu.tsx`
Menu de navigație global cu suport pentru admin/user roles

**Props:**
- `isAdmin?: boolean` - afișează link-uri admin

**Features:**
- Logo VitiScan
- Navigation links cu icons
- Admin badges pentru link-uri speciale
- User menu icon
- Responsive design

---

### `UIComponents.tsx`
Componente UI helper pentru consistency

**Exports:**
1. **StatusBadge** - badges pentru pending/approved/allow/deny
2. **MechanismBadge** - badges pentru RBAC/ABAC/ReBAC
3. **LoadingSpinner** - spinner reutilizabil (sm/md/lg)
4. **EmptyState** - state gol cu icon + title + action
5. **ErrorAlert** - alertă roșie pentru erori
6. **SuccessAlert** - alertă verde pentru success

---

## 🎨 Design System

### Culori
- **Primary:** Green-600 (#16a34a)
- **Success:** Green-100/800
- **Error:** Red-100/800
- **Warning:** Yellow-100/800
- **Info:** Blue-100/800
- **RBAC:** Blue-100/800
- **ABAC:** Purple-100/800
- **ReBAC:** Orange-100/800

### Typography
- **Headings:** Font-bold, text-gray-900
- **Body:** Text-gray-600
- **Mono:** Font-mono pentru IDs/tokens

### Spacing
- **Container:** max-w-7xl mx-auto
- **Section:** mb-6 sau mb-8
- **Form fields:** space-y-4 sau space-y-6

---

## 📱 Responsive Design

Toate paginile sunt 100% responsive:
- **Mobile:** Stack vertical, full width
- **Tablet:** Grid 2 coloane pentru forms
- **Desktop:** Grid 3-4 coloane pentru stats/cards

---

## 🔗 Integrare API

### Base URL
```typescript
const API_BASE = 'http://localhost:8000';
```

### Authentication
```typescript
headers: {
  'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
}
```

### Error Handling
Toate paginile au:
- Try/catch pentru fetch
- Error state cu mesaj user-friendly
- Loading states
- Fallback UI pentru failures

---

## ✅ Checklist Implementare

### Beta Onboarding
- [x] /beta-request page
- [x] /register-complete page
- [x] /admin/beta-requests page
- [x] Form validation
- [x] Success/Error states
- [x] Token verification

### Audit Logs
- [x] /admin/audit/logs page
- [x] Stats dashboard
- [x] Filtre avansate
- [x] Modal "Why?"
- [x] Mechanism/Outcome badges

### Authz Debugger
- [x] /authz/debug page
- [x] Scenarii predefinite
- [x] JSON editor
- [x] Dry run toggle
- [x] Response explicat

### Capability Tokens
- [x] /parcels/:id/share page
- [x] /view/:token page
- [x] Token generation form
- [x] One-time display
- [x] Copy to clipboard
- [x] Map integration
- [x] Error states

### Componente
- [x] NavigationMenu
- [x] StatusBadge
- [x] MechanismBadge
- [x] LoadingSpinner
- [x] EmptyState
- [x] ErrorAlert
- [x] SuccessAlert

### Types
- [x] authz.ts type definitions

---

## 🚀 Quick Start

### 1. Instalare dependențe (dacă lipsesc)
```bash
cd frontend
npm install axios
```

### 2. Configurare .env.local
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_IGN_API_KEY=essentiels
```

### 3. Rulare development
```bash
npm run dev
```

### 4. Test pagini
- http://localhost:3000/beta-request
- http://localhost:3000/register-complete?token=test123
- http://localhost:3000/admin/beta-requests
- http://localhost:3000/admin/audit/logs
- http://localhost:3000/authz/debug
- http://localhost:3000/parcels/123/share
- http://localhost:3000/view/token123

---

## 🎯 Next Steps (Optional)

1. **Integrare Context API pentru Auth**
   - useAuth() hook pentru JWT management
   - Protected routes wrapper
   - Auto-refresh token

2. **Real-time Updates (WebSockets)**
   - Audit logs live refresh
   - Beta requests notifications

3. **Export Features**
   - CSV export pentru audit logs
   - PDF report pentru beta requests

4. **Analytics Dashboard**
   - Charts pentru audit stats (Chart.js/Recharts)
   - Timeline pentru user activity

5. **Mobile App**
   - React Native version pentru token viewing
   - QR codes pentru tokens

---

## 📚 Resurse

- **Tailwind CSS:** https://tailwindcss.com/docs
- **Next.js App Router:** https://nextjs.org/docs/app
- **React Leaflet:** https://react-leaflet.js.org/
- **Authorization Docs:** ../backend/AUTHORIZATION_SYSTEM.md

---

**Status:** ✅ 100% Complete - Production Ready

**Created:** February 3, 2026  
**Version:** 1.0.0  
**Author:** VitiScan Development Team
