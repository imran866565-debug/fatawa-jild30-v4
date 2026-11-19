# Fatawa Razviya — Jild 30 tashreeh v4 merge

Merge workspace: 16 leaf chunk files of the easy-Urdu tashreeh v4 for Fatawa Razviya Jild 30 (volume_id 62; 218 items, 715 pages) are merged into `jild-30.json` by GitHub Actions (`merge_jild30_v4.py`), then published as a v1.0 release asset.

Item order reproduces the v3 merged file exactly (first jild30-pesh-lafz, last jild30-hadi-al-hayran-khatima). All 16 leaf chunks carry start_page == min(pages). The merge joins 7 two-part groups (masala-33, masala-35, fasl-2-wasl-1-hadith-71-95, p500, hadith-146, irshad-33, hadith-175) with no renames, then stable-sorts by start_page, matching the v3 merged file. No page markers are present in the chunks.
