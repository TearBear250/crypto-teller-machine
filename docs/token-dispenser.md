# CTM Souvenir Token Dispenser Requirements

This document defines requirements for the optional souvenir token dispenser feature of the Crypto Teller Machine (CTM).

> **Important legal notice:** The tokens described in this document are **novelty collectibles only**.  
> They have **no cash value**, are **not legal tender**, carry **no monetary denomination**, and **cannot be redeemed** for cash, cryptocurrency, goods, or services of any kind.  
> No token issued by this system may be represented to a user as having monetary value.

---

## 1. Core Constraints — Non-Negotiable

These constraints must be satisfied in all designs, labels, and software implementations:

1. **No face value.** Tokens must not display any dollar amount, coin denomination (e.g., "10¢", "25¢", "$1"), or any other monetary value indicator.
2. **No currency symbols in a value context.** Do not place "USD", "$", "€", "£", or equivalent symbols on tokens in a way that implies monetary worth.
3. **Prominent "no value" disclaimer.** Every token must carry text making clear it has no cash value. Suggested wording (choose one or combine):
   - "NO CASH VALUE"
   - "COLLECTIBLE ONLY"
   - "NOT LEGAL TENDER"
   - "SOUVENIR TOKEN"
4. **No redemption promise.** Tokens must not include wording that implies they can be exchanged for anything of value.
5. **No resemblance to legal tender.** Tokens must not imitate the design, size, shape, or markings of official government-issued coins or banknotes. Avoid designs that could be mistaken for coins currently in circulation.
6. **Consistent messaging in UI.** The Kiosk UI must describe tokens as "souvenir tokens" or "collectible tokens" — never as "coins of value", "crypto coins", "denomination tokens", or similar.

---

## 2. Suggested Token Design

Tokens are a fun, branded collectible to commemorate a CTM transaction. Design them accordingly.

### 2.1 Physical Specification (suggested, not final)

| Attribute | Suggested Value | Notes |
|---|---|---|
| Diameter | 32–40 mm | Distinct from any standard coin (US quarter = 24.3 mm; dollar = 26.5 mm) |
| Thickness | 2–3 mm | Thicker than legal tender coins to feel distinct |
| Material | Zinc alloy, aluminum, or acrylic | Not gold-colored if that might suggest monetary value |
| Edge | Reeded or smooth | Avoid designs matching real coin edges |
| Finish | Matte, brushed, or colored anodize | Visually distinct from minted government coins |

### 2.2 Obverse (Front) Design Elements

- **CTM logo or project name** as the primary graphic.
- **Coin brand icon** (e.g., Litecoin "Ł", Dogecoin "Ð", Solana sun logo, XRP wave) — used as a recognizable brand identifier, not a denomination mark.
  - Icon must be clearly artistic/stylized, not a replica of any official government currency imagery.
- **"COLLECTIBLE TOKEN"** or **"SOUVENIR"** text.
- Optional: year of issue.

### 2.3 Reverse (Back) Design Elements

- **"NO CASH VALUE"** — required, prominent placement, minimum character height 3 mm.
- **"NOT LEGAL TENDER"** — required.
- Coin name in words (e.g., "LITECOIN", "DOGECOIN") as a brand label — not as a value statement.
- Optional: decorative border, website URL, or QR code to a "what is this token?" informational page.
- Optional: serial or batch number for tracking.

### 2.4 Design Review Checklist

Before approving a token design for production:

- [ ] No monetary amount or currency denomination present.
- [ ] "NO CASH VALUE" text is prominent and legible (≥ 3 mm character height).
- [ ] "NOT LEGAL TENDER" text is present.
- [ ] Token dimensions are distinct from any currently-circulating government coin.
- [ ] Design does not replicate or closely imitate any government-issued coin or banknote.
- [ ] No redemption language present.
- [ ] Legal review completed in jurisdictions where tokens will be dispensed.

---

## 3. Dispenser Hardware Requirements

### 3.1 Mechanism Type

- Use a standard **coin/token hopper dispenser** compatible with the specified token dimensions.
- The hopper must be physically enclosed (no exposed moving parts accessible to users).
- Token delivery must use a **chute or track** that deposits the token in a secure pocket or tray, not a free-fall slot that could trap fingers.

### 3.2 Interlocks

- The token dispenser **must** follow the same interlock rules as the cash dispenser (see [`docs/safety.md`](safety.md)).
- Specifically:
  - Dispenser must be disabled by default.
  - The device daemon must control the enable signal through a driver board (not direct GPIO).
  - Jam detection must halt the mechanism and flag a fault without retrying.

### 3.3 Configurable Quantity

- The device daemon must support configuring whether a token is dispensed per transaction (or not at all).
- Dispense quantity per transaction: default 1; configurable up to a small maximum (e.g., 3).
- The system must track hopper fill level and alert operators when tokens are running low.

---

## 4. Kiosk UI Requirements

- During a cash-out transaction, if the token dispenser is enabled, show a screen or overlay:
  - Title: **"Your Souvenir Token"** (or "Collectible Token").
  - Body: **"Enjoy this complimentary collectible token. It has no cash value and is not legal tender."**
  - An icon of the coin brand associated with the transaction (optional, for visual delight).
- The UI must never present the token as a representation of the user's cryptocurrency or as having monetary worth.
- If the dispenser is out of tokens or faulted, skip the token silently or show a brief "Sorry, token unavailable" note — do not block the transaction.

---

## 5. Related Regulations (Informational)

> This section is informational only and not legal advice. Consult a lawyer in your jurisdiction.

- **United States:** Tokens that do not imitate government coins and carry "no cash value" markings are generally permissible as novelties under 18 U.S.C. § 336 (prohibition on making/possessing metal tokens for use as money). Ensure tokens are not designed to defraud.
- **Other jurisdictions:** Check local laws on token issuance, gaming/gambling regulations (if tokens could be associated with gaming), and consumer protection rules.
- **Cryptocurrency branding:** Using a cryptocurrency project's logo/icon as decoration is subject to each project's trademark policy. Review licensing before production.
