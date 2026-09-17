# Privacy Policy for BharatMandi (भारत मंडी)

**Effective Date:** September 17, 2026  
**Last Updated:** September 17, 2026  
**Developer:** SystemicLogics  
**Application:** BharatMandi (Package: `com.bharatmandi.kisan`)

---

## 1. Introduction

Welcome to **BharatMandi (भारत मंडी)**. We are committed to protecting the privacy of our users—farmers, traders, commission agents, and agricultural community members across India.

This Privacy Policy explains how our mobile application handles user information and permissions in full compliance with the **Google Play Developer Program Policies** and the **Google Play User Data Policy**.

---

## 2. Information We Collect and How It Is Used

BharatMandi is designed with a **privacy-first, offline-first** architecture. We do not require account registration, phone numbers, email addresses, or payment details to browse mandi rates.

### A. Location Data (`ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`)
* **Purpose:** When you tap **"Find Near Mandi" (पास की मंडी खोजें)**, the app accesses your device's location to determine your proximity to nearby APMC mandi yards and sort daily commodity rates by distance.
* **On-Device Processing:** Location data is processed entirely **on your device in real-time**.
* **Zero Tracking / Zero Logging:** We **never** transmit, store, track, sell, or share your GPS coordinates on external tracking servers or with advertising networks.
* **Pincode Alternative:** If you choose not to share GPS location, you can manually enter any 6-digit Indian pincode to find nearest mandis without granting location permissions.

### B. Microphone & Audio Data (`RECORD_AUDIO`)
* **Purpose:** When you tap the **Microphone (बोलकर खोजें)** icon, the app accesses the microphone strictly to transcribe spoken words (e.g., *"गेहूं का भाव"* or *"नीमच मंडी"*) into search text.
* **Transient Processing:** Speech-to-text processing occurs transiently using your device's native speech recognition system.
* **No Recording Stored:** Audio recordings are **never** saved, recorded to disk, or transmitted to any proprietary servers.

### C. Storage & File Sharing
* **Purpose:** When you choose to share a mandi rate card with farmer groups or traders via WhatsApp or other apps, the app renders a visual summary card and saves a temporary image to your device cache for sharing.
* **No Personal File Access:** The app does not access your personal photos, documents, contacts, or media gallery.

### D. Network Data & Live Mandi Rates
* **Purpose:** The app connects to our public GitHub CDN repository (`systemiclogics-beep/mandi-rates`) over secure HTTPS to download verified daily APMC mandi rates sourced from official public agricultural portals (Agmarknet and data.gov.in).
* **No Telemetry Tracking:** No personal usage telemetry or device identifiers are collected during rate synchronization.

---

## 3. Data Sharing and Third-Party Disclosure

* We **do not sell, rent, trade, or monetize** your personal or device data.
* We **do not use** third-party advertising SDKs or tracking cookies.
* We do not share data with any commercial third parties.

---

## 4. Data Retention and Deletion

* All offline rate records, user-selected language preferences, and starred favorites are stored locally on your device in a secure SQLite database.
* You can delete all locally stored data at any time by:
  1. Opening your phone's **Settings > Apps > BharatMandi > Storage**.
  2. Tapping **Clear Data** or **Clear Cache**.
  3. Or simply uninstalling the application.

---

## 5. Children's Privacy

BharatMandi is an agricultural market utility app and does not target or knowingly collect information from children under the age of 13.

---

## 6. Security

We follow industry-standard security practices. All remote network communications for mandi rate updates occur over encrypted HTTPS channels. No sensitive user credentials or personal databases are maintained on remote servers.

---

## 7. Changes to This Privacy Policy

We may update our Privacy Policy periodically to reflect new features or legal requirements. Any modifications will be posted directly to this page with an updated effective date.

---

## 8. Contact Us

If you have any questions, suggestions, or concerns regarding this Privacy Policy or the data practices of BharatMandi, please contact us:

* **Developer:** SystemicLogics
* **Email:** systemiclogics@gmail.com
