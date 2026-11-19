#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 30 easy-Urdu tashreeh v4 chunks into jild-30.json.

Reads the 16 leaf chunk files listed in chunks-manifest-v4-jild30.json,
concatenates them in order 01 -> 02 -> ... -> 16, JOINS the 7
two-part groups below into single items, STABLE SORTS by start_page
(mirroring the v3 merge), derives start_page = min(pages) where the
field is absent (0 derived: all chunks carry start_page), normalises
page markers (0 present), validates, and writes {"masail": [...]} to
jild-30.json.

ORDER -- chunk order is the order, then a stable sort by start_page:
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-30.json
  has ID order == stable sort by start_page of the concatenation
  (verified: the v3 order IS the stable sort, including its tied
  start_pages). Do NOT sort or reorder before the joins.
  Within each chunk, items keep file order.
  CHUNK_ORDER is an explicit 16-leaf list.

JOINS (7): parts are found BY (id, start_page) selectors, in page
  order. Join rule PROVED from the v3 chunk files (J25 method): ""
  join of the stripped part jawabs == the merged v3 jawab EXACTLY
  for all 7 (" " join fails all 7). Sawal: the FIRST part's sawal
  (all tails have empty sawal; v3 proves head sawal == merged sawal
  for masala-33/35). Title: the part whose title == the merged-v3
  title (exactly one per join — for 6 of the 7 the FIRST part; for
  jild30-p500 the SECOND part). Pages: sorted union.
  Notes: concatenation in order.
    masala-33   [129-178] + [179-185] -> [129-185], 57pp, sawal 618
    masala-35   [359-408] + [409-422] -> [359-422], 64pp, sawal 3877
    fasl-2-wasl-1-hadith-71-95 [436-458] + [459] -> [436-459], 24pp
    p500        [499] + [500-506] -> [499-506], 8pp (title from tail)
    hadith-146  [547-549] + [550-551] -> [547-551], 5pp
    irshad-33   [228] + [229] -> [228-229], 2pp (same-id)
    hadith-175  [598-599] + [600-604] -> [598-604], 7pp (same-id)
  After the joins there are 218 items and 218 unique ids. NO
  renames at merge. The 5 absorbed ids (ayat-ashira, ayat-19-40,
  aman-hadith-95, aman-hadith-129-start, p547) are gone.
  All chunks carry start_page == min(pages) (0 derived). Pages are
  shared between items by design (a boundary page belongs to two
  items): present pages 903, unique pages 715 — every page assertion
  uses SETS.

EMPTY JAWAB: exactly one — jild30-hadi-al-hayran-fasl-dawwam-sawal
  (empty in v3 too; allow-listed, nothing invented).
EMPTY SAWAL after the merge: 183 (== v3, all by design).
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild30.json"

# Concatenation order: chunk files 01 -> 16, in order.
CHUNK_ORDER = ["jild-30-chunk-01.json", "jild-30-chunk-02.json", "jild-30-chunk-03.json", "jild-30-chunk-04.json", "jild-30-chunk-05.json", "jild-30-chunk-06.json", "jild-30-chunk-07.json", "jild-30-chunk-08.json", "jild-30-chunk-09.json", "jild-30-chunk-10.json", "jild-30-chunk-11.json", "jild-30-chunk-12.json", "jild-30-chunk-13.json", "jild-30-chunk-14.json", "jild-30-chunk-15.json", "jild-30-chunk-16.json"]

EXPECTED_ITEMS = 218
EXPECTED_PAGES = 715
EXPECTED_MIN_PAGE = 5
EXPECTED_MAX_PAGE = 772
EXPECTED_VOLUME_IDS = {62}
EXPECTED_FIRST_ID = "jild30-pesh-lafz"
EXPECTED_LAST_ID = "jild30-hadi-al-hayran-khatima"

# v3 ID sequence, verbatim from content/tashreeh/jild-30.json.
V3_IDS = ["jild30-pesh-lafz", "jild30-tahdees-e-nemat", "jild30-masala-1-4", "jild30-masala-5", "jild30-masala-6", "jild30-masala-7", "jild30-masala-8", "jild30-masala-9", "jild30-masala-10", "jild30-masala-11", "jild30-masala-12", "jild30-masala-13-20", "jild30-masala-21", "jild30-masala-22", "jild30-masala-23", "jild30-masala-24", "jild30-masala-25", "jild30-masala-26", "jild30-masala-27", "jild30-masala-28", "jild30-masala-29", "jild30-masala-30", "jild30-masala-31", "jild30-masala-32", "jild30-masala-33", "jild30-haikal-2-tabish-1-wahi", "jild30-tabish-2-jalwa-1-irshad-1-14", "jild30-tabish-2-jalwa-2-irshad-15-26", "jild30-irshad-27", "jild30-irshad-28-32", "jild30-irshad-33", "jild30-irshad-34", "jild30-irshad-35", "jild30-irshad-36", "jild30-irshad-37", "jild30-irshad-38", "jild30-irshad-39", "jild30-irshad-40", "jild30-irshad-41", "jild30-irshad-42", "jild30-irshad-43", "jild30-irshad-44", "jild30-irshad-45", "jild30-irshad-46", "jild30-irshad-47", "jild30-irshad-48", "jild30-irshad-49", "jild30-irshad-50", "jild30-irshad-51", "jild30-irshad-52", "jild30-irshad-53", "jild30-tabish-3", "jild30-tabish-4-riwayat-1", "jild30-tabish-4-riwayat-2", "jild30-tabish-4-riwayat-3", "jild30-tabish-4-riwayat-4", "jild30-tabish-4-riwayat-5", "jild30-tabish-4-riwayat-6", "jild30-tabish-4-riwayat-7", "jild30-tabish-4-riwayat-8", "jild30-tabish-4-riwayat-9", "jild30-tabish-4-riwayat-10", "jild30-tabish-4-riwayat-11", "jild30-tabish-4-riwayat-12", "jild30-noor-khitam", "jild30-tanbih", "jild30-risala-khatima", "jild30-bisharat-jalila", "jild30-bisharat-uzma", "jild30-masala-34", "jild30-masala-34-dalil-2", "jild30-masala-34-dalil-3", "jild30-masala-34-dalil-4", "jild30-masala-34-dalil-5", "jild30-masala-34-dalil-6", "jild30-masala-34-dalil-7", "jild30-masala-34-dalil-8-9", "jild30-masala-34-dalil-10", "jild30-masala-34-tanbeehat", "jild30-masala-34-maslak-nukta", "jild30-masala-34-faida", "jild30-masala-34-aida", "jild30-masala-34-ibrat-khatima", "jild30-tamheed-iman-01", "jild30-tamheed-iman-02", "jild30-tamheed-iman-03", "jild30-tamheed-iman-04", "jild30-tamheed-iman-05", "jild30-tamheed-iman-06", "jild30-tamheed-iman-07", "jild30-tamheed-iman-08", "jild30-tamheed-iman-09", "jild30-tamheed-iman-10", "jild30-tamheed-iman-11", "jild30-tamheed-iman-12", "jild30-tamheed-iman-13", "jild30-tamheed-iman-14", "jild30-tamheed-iman-15", "jild30-tamheed-iman-16", "jild30-tamheed-iman-17", "jild30-tamheed-iman-18", "jild30-tamheed-iman-19", "jild30-masala-35", "jild30-ayat-41-43-tawrat-zabur", "jild30-faida-azeema", "jild30-ayat-44-45-hadith-61-70-mafatih", "jild30-fasl-2-wasl-1-hadith-71-95", "jild30-aman-hadith-96-98", "jild30-aman-hadith-99", "jild30-aman-hadith-100-102", "jild30-aman-hadith-103-105", "jild30-aman-hadith-106-111", "jild30-aman-hadith-112-114", "jild30-aman-hadith-115-117", "jild30-aman-hadith-118-120", "jild30-aman-hadith-121-123", "jild30-aman-hadith-124-125", "jild30-aman-hadith-126", "jild30-aman-ahadith-bad-126", "jild30-aman-ghawth-azam", "jild30-aman-hadith-127", "jild30-aman-hadith-128", "jild30-p500", "jild30-p506", "jild30-p511", "jild30-p519", "jild30-p525", "jild30-hadith-146", "jild30-hadith-147", "jild30-hadith-148", "jild30-hadith-149", "jild30-hadith-150", "jild30-hadith-151-152", "jild30-hadith-153", "jild30-hadith-154-155", "jild30-hadith-156", "jild30-hadith-157", "jild30-hadith-158", "jild30-hadith-159", "jild30-hadith-160", "jild30-hadith-161", "jild30-hadith-162", "jild30-hadith-163", "jild30-hadith-164", "jild30-hadith-165", "jild30-hadith-166", "jild30-hadith-167", "jild30-hadith-168", "jild30-hadith-169", "jild30-hadith-170", "jild30-hadith-171", "jild30-hadith-172", "jild30-hadith-173", "jild30-hadith-174", "jild30-hadith-175", "jild30-hadith-176", "jild30-hadith-177", "jild30-hadith-178-179", "jild30-hadith-180", "jild30-hadith-181", "jild30-hadith-182", "jild30-hadith-183", "jild30-hadith-184", "jild30-hadith-185", "jild30-hadith-186", "jild30-hadith-187", "jild30-hadith-188", "jild30-hadith-189", "jild30-hadith-190", "jild30-hadith-191", "jild30-hadith-192", "jild30-hadith-193", "jild30-hadith-194", "jild30-hadith-195", "jild30-wasl-3", "jild30-hadith-196", "jild30-hadith-197", "jild30-hadith-198", "jild30-hadith-199", "jild30-hadith-200", "jild30-hadith-201", "jild30-hadith-202", "jild30-hadith-203", "jild30-hadith-204", "jild30-hadith-205", "jild30-hadith-206", "jild30-hadith-207", "jild30-hadith-208", "jild30-hadith-209", "jild30-hadith-210", "jild30-takmila-kamila", "jild30-hadith-211", "jild30-hadith-212", "jild30-hadith-213", "jild30-hadith-214", "jild30-hadith-215", "jild30-hadith-216", "jild30-hadith-217", "jild30-hadith-218", "jild30-masala-36", "jild30-masala-37", "jild30-masala-38", "jild30-masala-39", "jild30-masala-40", "jild30-masala-41", "jild30-masala-42", "jild30-taqreez", "jild30-masala-43", "jild30-masala-44", "jild30-hadi-al-hayran-ibtidaiya", "jild30-hadi-al-hayran-fasl-awwal-muqaddimat", "jild30-hadi-al-hayran-fasl-awwal-radd-1", "jild30-hadi-al-hayran-fasl-awwal-radd-2", "jild30-hadi-al-hayran-fasl-dawwam-sawal", "jild30-hadi-al-hayran-fasl-dawwam-jawab-1", "jild30-hadi-al-hayran-fasl-dawwam-jawab-2", "jild30-hadi-al-hayran-fasl-dawwam-jawab-3", "jild30-hadi-al-hayran-khatima"]

# v3 pages per item id, verbatim from content/tashreeh/jild-30.json.
V3_PAGES = {
    "jild30-pesh-lafz": [5, 6, 7, 8, 9, 10, 11],
    "jild30-tahdees-e-nemat": [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
    "jild30-masala-1-4": [71, 72, 73, 74, 75, 76, 77, 78],
    "jild30-masala-5": [78, 79, 80, 81],
    "jild30-masala-6": [81, 82],
    "jild30-masala-7": [83],
    "jild30-masala-8": [83, 84, 85],
    "jild30-masala-9": [85, 86, 87, 88, 89, 90, 92],
    "jild30-masala-10": [93],
    "jild30-masala-11": [94],
    "jild30-masala-12": [94],
    "jild30-masala-13-20": [95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
    "jild30-masala-21": [110, 111],
    "jild30-masala-22": [113, 114, 115],
    "jild30-masala-23": [115, 116],
    "jild30-masala-24": [116, 117, 118],
    "jild30-masala-25": [118, 119, 120],
    "jild30-masala-26": [121],
    "jild30-masala-27": [121, 122],
    "jild30-masala-28": [122, 123],
    "jild30-masala-29": [123],
    "jild30-masala-30": [123, 124],
    "jild30-masala-31": [125, 126, 127],
    "jild30-masala-32": [127, 128],
    "jild30-masala-33": [129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185],
    "jild30-haikal-2-tabish-1-wahi": [185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198],
    "jild30-tabish-2-jalwa-1-irshad-1-14": [198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208],
    "jild30-tabish-2-jalwa-2-irshad-15-26": [208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218],
    "jild30-irshad-27": [218, 219, 220, 221, 222, 223, 224, 225],
    "jild30-irshad-28-32": [226, 227, 228],
    "jild30-irshad-33": [228, 229],
    "jild30-irshad-34": [229],
    "jild30-irshad-35": [229, 230],
    "jild30-irshad-36": [231],
    "jild30-irshad-37": [231, 232],
    "jild30-irshad-38": [232, 233],
    "jild30-irshad-39": [233],
    "jild30-irshad-40": [233, 234],
    "jild30-irshad-41": [234, 235],
    "jild30-irshad-42": [235],
    "jild30-irshad-43": [235, 236],
    "jild30-irshad-44": [236, 237],
    "jild30-irshad-45": [237],
    "jild30-irshad-46": [237, 238],
    "jild30-irshad-47": [238, 239, 240, 241, 242, 243],
    "jild30-irshad-48": [243],
    "jild30-irshad-49": [243, 244],
    "jild30-irshad-50": [244],
    "jild30-irshad-51": [244],
    "jild30-irshad-52": [244, 245],
    "jild30-irshad-53": [245, 246],
    "jild30-tabish-3": [246, 247, 248, 249, 250, 251, 252, 253, 254],
    "jild30-tabish-4-riwayat-1": [254, 255],
    "jild30-tabish-4-riwayat-2": [254, 255],
    "jild30-tabish-4-riwayat-3": [255],
    "jild30-tabish-4-riwayat-4": [255, 256],
    "jild30-tabish-4-riwayat-5": [255, 256],
    "jild30-tabish-4-riwayat-6": [256, 257],
    "jild30-tabish-4-riwayat-7": [257],
    "jild30-tabish-4-riwayat-8": [257, 258],
    "jild30-tabish-4-riwayat-9": [258, 259],
    "jild30-tabish-4-riwayat-10": [259],
    "jild30-tabish-4-riwayat-11": [259],
    "jild30-tabish-4-riwayat-12": [259, 260, 261],
    "jild30-noor-khitam": [261, 262],
    "jild30-tanbih": [262, 263],
    "jild30-risala-khatima": [263, 264],
    "jild30-bisharat-jalila": [265, 266],
    "jild30-bisharat-uzma": [266],
    "jild30-masala-34": [267, 268, 269],
    "jild30-masala-34-dalil-2": [269, 270, 271],
    "jild30-masala-34-dalil-3": [271],
    "jild30-masala-34-dalil-4": [271, 272, 273, 274, 275],
    "jild30-masala-34-dalil-5": [275, 276],
    "jild30-masala-34-dalil-6": [276, 277, 278, 279, 280],
    "jild30-masala-34-dalil-7": [280, 281],
    "jild30-masala-34-dalil-8-9": [281, 282, 283],
    "jild30-masala-34-dalil-10": [283, 284],
    "jild30-masala-34-tanbeehat": [284, 285, 286, 287, 288],
    "jild30-masala-34-maslak-nukta": [288, 289, 290, 291, 292, 293, 294, 295, 296, 297],
    "jild30-masala-34-faida": [297, 298, 299, 300, 301],
    "jild30-masala-34-aida": [301, 302, 303],
    "jild30-masala-34-ibrat-khatima": [303, 304, 305],
    "jild30-tamheed-iman-01": [307],
    "jild30-tamheed-iman-02": [308, 309],
    "jild30-tamheed-iman-03": [309, 310],
    "jild30-tamheed-iman-04": [310, 311],
    "jild30-tamheed-iman-05": [311, 312],
    "jild30-tamheed-iman-06": [313, 314],
    "jild30-tamheed-iman-07": [315],
    "jild30-tamheed-iman-08": [316, 317],
    "jild30-tamheed-iman-09": [317, 318, 319, 320],
    "jild30-tamheed-iman-10": [320, 321],
    "jild30-tamheed-iman-11": [321, 322],
    "jild30-tamheed-iman-12": [322, 323, 324],
    "jild30-tamheed-iman-13": [324, 325, 326],
    "jild30-tamheed-iman-14": [326, 327, 328, 329, 330, 331],
    "jild30-tamheed-iman-15": [331, 332, 333, 334, 335, 336, 337, 338, 339],
    "jild30-tamheed-iman-16": [339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349],
    "jild30-tamheed-iman-17": [349, 350],
    "jild30-tamheed-iman-18": [350, 351, 352, 353, 354, 355, 356, 357],
    "jild30-tamheed-iman-19": [357, 358],
    "jild30-masala-35": [359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422],
    "jild30-ayat-41-43-tawrat-zabur": [422, 423, 424, 425],
    "jild30-faida-azeema": [425, 426],
    "jild30-ayat-44-45-hadith-61-70-mafatih": [426, 427, 428, 429, 430, 431, 432, 433, 434, 435],
    "jild30-fasl-2-wasl-1-hadith-71-95": [436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459],
    "jild30-aman-hadith-96-98": [460, 461, 462],
    "jild30-aman-hadith-99": [462, 463, 464, 465],
    "jild30-aman-hadith-100-102": [465, 466, 467],
    "jild30-aman-hadith-103-105": [467, 468, 469, 470],
    "jild30-aman-hadith-106-111": [470, 471, 472],
    "jild30-aman-hadith-112-114": [472, 473, 474, 475, 476],
    "jild30-aman-hadith-115-117": [476, 477, 478],
    "jild30-aman-hadith-118-120": [478, 479, 480],
    "jild30-aman-hadith-121-123": [480, 481, 482, 483],
    "jild30-aman-hadith-124-125": [483, 484, 485],
    "jild30-aman-hadith-126": [485, 486, 487, 488],
    "jild30-aman-ahadith-bad-126": [489, 490, 491],
    "jild30-aman-ghawth-azam": [491, 492, 493],
    "jild30-aman-hadith-127": [493, 494, 495, 496],
    "jild30-aman-hadith-128": [496, 497, 498, 499],
    "jild30-p500": [499, 500, 501, 502, 503, 504, 505, 506],
    "jild30-p506": [506, 507, 508, 509, 510, 511],
    "jild30-p511": [511, 512, 513, 514, 515, 516, 517, 518, 519],
    "jild30-p519": [519, 520, 521, 522, 523, 524],
    "jild30-p525": [525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547],
    "jild30-hadith-146": [547, 548, 549, 550, 551],
    "jild30-hadith-147": [551, 552, 553],
    "jild30-hadith-148": [553],
    "jild30-hadith-149": [553, 554],
    "jild30-hadith-150": [554],
    "jild30-hadith-151-152": [554],
    "jild30-hadith-153": [555],
    "jild30-hadith-154-155": [555, 556],
    "jild30-hadith-156": [556],
    "jild30-hadith-157": [556],
    "jild30-hadith-158": [556, 557, 558],
    "jild30-hadith-159": [558],
    "jild30-hadith-160": [558, 559, 560],
    "jild30-hadith-161": [559],
    "jild30-hadith-162": [559, 560],
    "jild30-hadith-163": [560],
    "jild30-hadith-164": [560],
    "jild30-hadith-165": [560, 561, 562],
    "jild30-hadith-166": [562, 563],
    "jild30-hadith-167": [563, 564, 565, 566],
    "jild30-hadith-168": [566, 567, 568, 569, 570, 571, 572, 573, 574, 575],
    "jild30-hadith-169": [575, 576],
    "jild30-hadith-170": [576, 577, 578, 579, 580, 581],
    "jild30-hadith-171": [581, 582, 583, 584],
    "jild30-hadith-172": [584],
    "jild30-hadith-173": [584, 585],
    "jild30-hadith-174": [585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598],
    "jild30-hadith-175": [598, 599, 600, 601, 602, 603, 604],
    "jild30-hadith-176": [604, 605],
    "jild30-hadith-177": [605],
    "jild30-hadith-178-179": [606, 607],
    "jild30-hadith-180": [607],
    "jild30-hadith-181": [607, 608],
    "jild30-hadith-182": [608],
    "jild30-hadith-183": [608, 609, 610, 611],
    "jild30-hadith-184": [611],
    "jild30-hadith-185": [612, 613],
    "jild30-hadith-186": [613],
    "jild30-hadith-187": [613, 614],
    "jild30-hadith-188": [614, 615],
    "jild30-hadith-189": [615, 616],
    "jild30-hadith-190": [616, 617],
    "jild30-hadith-191": [617],
    "jild30-hadith-192": [617, 618],
    "jild30-hadith-193": [618],
    "jild30-hadith-194": [618, 619],
    "jild30-hadith-195": [619],
    "jild30-wasl-3": [619],
    "jild30-hadith-196": [619, 620],
    "jild30-hadith-197": [619, 620],
    "jild30-hadith-198": [620, 621],
    "jild30-hadith-199": [621],
    "jild30-hadith-200": [621, 622],
    "jild30-hadith-201": [622, 623],
    "jild30-hadith-202": [623],
    "jild30-hadith-203": [624],
    "jild30-hadith-204": [624],
    "jild30-hadith-205": [624, 625],
    "jild30-hadith-206": [625, 626],
    "jild30-hadith-207": [626],
    "jild30-hadith-208": [626, 627],
    "jild30-hadith-209": [627],
    "jild30-hadith-210": [627, 628, 629],
    "jild30-takmila-kamila": [629],
    "jild30-hadith-211": [629, 630],
    "jild30-hadith-212": [630, 631],
    "jild30-hadith-213": [631, 632],
    "jild30-hadith-214": [632],
    "jild30-hadith-215": [632],
    "jild30-hadith-216": [632, 633],
    "jild30-hadith-217": [633, 634],
    "jild30-hadith-218": [634, 635],
    "jild30-masala-36": [637, 638, 639, 640, 641, 642, 643],
    "jild30-masala-37": [643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655],
    "jild30-masala-38": [657, 658, 659, 660],
    "jild30-masala-39": [660, 661, 662],
    "jild30-masala-40": [662, 663],
    "jild30-masala-41": [663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680],
    "jild30-masala-42": [680, 681, 682, 683, 684, 685, 686],
    "jild30-taqreez": [687, 688, 689, 690, 691, 692, 693, 694],
    "jild30-masala-43": [695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 713, 714],
    "jild30-masala-44": [715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736],
    "jild30-hadi-al-hayran-ibtidaiya": [737, 738],
    "jild30-hadi-al-hayran-fasl-awwal-muqaddimat": [738, 739, 740, 741],
    "jild30-hadi-al-hayran-fasl-awwal-radd-1": [741, 742, 743, 744, 745, 746],
    "jild30-hadi-al-hayran-fasl-awwal-radd-2": [746, 747, 748, 749, 750, 751],
    "jild30-hadi-al-hayran-fasl-dawwam-sawal": [751, 752],
    "jild30-hadi-al-hayran-fasl-dawwam-jawab-1": [752, 753, 754, 755, 756, 757, 758, 759],
    "jild30-hadi-al-hayran-fasl-dawwam-jawab-2": [759, 760, 761, 762, 763, 764, 765],
    "jild30-hadi-al-hayran-fasl-dawwam-jawab-3": [765, 766, 767, 768, 769],
    "jild30-hadi-al-hayran-khatima": [769, 770, 771, 772],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 16, f"expected 16 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (none expected: all chunks carry start_page).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        # Jild 30 has no missing-notes quirk: every leaf item carries
        # a "notes" key (asserted here); nothing to normalise.
        for it in items:
            assert "notes" in it, f"{it['id']}: missing notes key"
        all_items.extend(items)

    # JOINS (7): two-part merges. Join rule PROVED from the v3
    # chunk files: "" join of the stripped part jawabs == the
    # merged v3 jawab EXACTLY for all 7 (" " join fails all 7).
    # Sawal: the FIRST part's sawal (all tails empty sawal).
    # Title: the part whose title == the merged-v3 title
    # (exactly one per join — for 6 of the 7 the FIRST part,
    # for jild30-p500 the SECOND part; the id-matching rule
    # FAILS for hadith-146, whose tail carries a different
    # title). Pages: sorted union.
    # Notes: concatenation in order. NO renames at merge.
    # Absorbed ids (5) must be gone: ayat-ashira, ayat-19-40,
    # aman-hadith-95, aman-hadith-129-start, p547.

    def join_parts(result_id, selectors, seam_checks, expected_jawab_len):
        parts = []
        used = set()
        for sel_id, sel_start in selectors:
            hits = [it for it in all_items
                    if it["id"] == sel_id
                    and (sel_start is None or it.get("start_page") == sel_start)
                    and id(it) not in used]
            assert hits, f"{result_id}: no part matched ({sel_id}, {sel_start})"
            for it in hits:
                used.add(id(it))
            parts.extend(hits)
        parts.sort(key=lambda it: min(it["pages"]))
        assert [min(p["pages"]) for p in parts] == sorted(min(p["pages"]) for p in parts), (
            f"{result_id}: parts not in page order"
        )
        vols = {p.get("volume_id") for p in parts}
        assert vols == EXPECTED_VOLUME_IDS, f"{result_id}: volume mismatch {vols}"
        assert all(p.get("tashreeh_jawab") for p in parts), (
            f"{result_id}: a part jawab is empty"
        )
        assert all(not p.get("tashreeh_sawal") for p in parts[1:]), (
            f"{result_id}: a tail part sawal is non-empty"
        )
        sawal = parts[0].get("tashreeh_sawal") or ""
        # (No v4-sawal == v3-sawal check: v4 rewrites the sawal;
        # the rule itself is proved from the v3 chunks.)
        for part_no, which, needle in seam_checks:
            txt = parts[part_no].get("tashreeh_jawab") or ""
            if which == "end":
                assert txt.rstrip().endswith(needle), (
                    f"{result_id} part {part_no + 1} end seam mismatch: ...{txt.rstrip()[-60:]!r}"
                )
            else:
                assert txt.lstrip().startswith(needle), (
                    f"{result_id} part {part_no + 1} start seam mismatch: {txt.lstrip()[:60]!r}"
                )
        title_parts = [p for p in parts if p["title"] == V3_TITLES[result_id]]
        assert len(title_parts) == 1, (
            f"{result_id}: {len(title_parts)} parts carry the v3 title, expected exactly 1"
        )
        title = title_parts[0]["title"]
        pages = sorted({p for part in parts for p in part["pages"]})
        assert pages == V3_PAGES[result_id], f"{result_id}: combined pages != v3"
        joined = {
            "id": result_id,
            "title": title,
            "volume_id": parts[0]["volume_id"],
            "pages": pages,
            "start_page": min(pages),
            "tashreeh_sawal": sawal,
            "tashreeh_jawab": "".join(p["tashreeh_jawab"].strip() for p in parts),
            "notes": [n for p in parts for n in p.get("notes", [])],
        }
        assert len(joined["tashreeh_jawab"]) == expected_jawab_len, (
            f"{result_id}: joined jawab {len(joined['tashreeh_jawab'])} chars != expected {expected_jawab_len}"
        )
        assert joined["tashreeh_jawab"], f"{result_id}: combined jawab is empty"
        idxs = [i for i, it in enumerate(all_items) if any(it is p for p in parts)]
        assert len(idxs) == len(parts), f"{result_id}: part index mismatch"
        first = idxs[0]
        for i in reversed(idxs[1:]):
            del all_items[i]
        all_items[first] = joined
        print(f"joined {result_id}: {len(parts)} parts -> 1 item, {len(pages)} pages, sawal {len(sawal)} chars, jawab {expected_jawab_len} chars, notes {len(joined['notes'])}")

    V3_TITLES = {
        "jild30-masala-33": "مسئلہ ۳۳: حضور صلی الله علیہ وسلم کا افضل المرسلین و سید المرسلین ہونا — رسالہ تجلی الیقین بانّ نبینا سید المرسلین",
        "jild30-masala-35": "مسئلہ ۳۵ — درودِ تاج و دلائل الخیرات اور «دافع البلاء» (رسالہ الامن و العلٰی لناعتی المصطفٰی بدافع البلاء)",
        "jild30-fasl-2-wasl-1-hadith-71-95": "فصل دوم، وصل اول — حدیث ۷۱ تا ۹۵",
        "jild30-p500": "رسالہ ضمنی «منیۃ اللبیب ان التشریح بید الحبیب» — احادیثِ تحریمِ حرمِ مدینہ (حدیث ۱۳۰ تا ۱۴۵)",
        "jild30-hadith-146": "حدیث ۱۴۶ — مسحِ موزہ کی مدت (مسافر تین راتیں)",
        "jild30-irshad-33": "ارشاد سی و سوم (۳۳) — قیامت میں ہر نبی کا منبر نور (سر کا حصہ)",
        "jild30-hadith-175": "حدیث ۱۷۵ — وصل دوم: اعرابی کا سوال اور بنی اسرائیل کی پیرزن",
    }

    join_parts(
        "jild30-masala-33",
        [('jild30-masala-33', None), ('jild30-ayat-ashira', None)],
        [
            (0, "end", "ں — ظہیر کا مطلب ہے مددگار — اور اس کے بعد کے امتیازات صفحہ ۱۷۸ سے آگے جاری ہیں۔"),
            (1, "start", "یہ حصہ آیت عاشرہ کا تسلسل ہے، تسلسل کا مطلب ہے پہلے سے چلی آ رہی بات کا آگے بڑھن"),
        ],
        70330,
    )
    join_parts(
        "jild30-masala-35",
        [('jild30-masala-35', None), ('jild30-ayat-19-40', None)],
        [
            (0, "end", "ں اور اس کے بعد فصل دوم کی دو سو چالیس حدیثیں اور خاتمہ اگلے chunks میں آئیں گے۔"),
            (1, "start", "یہ حصہ قرآن کریم کی ان آیتوں کا سلسلہ ہے جو حضور نبی کریم صلی اللہ تعالیٰ علیہ و"),
        ],
        59920,
    )
    join_parts(
        "jild30-fasl-2-wasl-1-hadith-71-95",
        [('jild30-fasl-2-wasl-1-hadith-71-95', None), ('jild30-aman-hadith-95', None)],
        [
            (0, "end", "ر سرخ تھے، اور یہیں صفحہ ۴۵۸ ختم ہو جاتا ہے، حدیث کا باقی حصہ چنک ۱۰ میں آئے گا۔"),
            (1, "start", "یہ صفحہ حدیث ۹۵ کے آخری حصے سے شروع ہوتا ہے: صحابہ کرام نے حضور اقدس صلی اللہ تع"),
        ],
        29127,
    )
    join_parts(
        "jild30-p500",
        [('jild30-aman-hadith-129-start', None), ('jild30-p500', None)],
        [
            (0, "end", " کا مطلب ہے حدیث پہنچانے والوں کی کڑی، اور مستفاد کا مطلب ہے حاصل ہونے والی بات۔"),
            (1, "start", "صفحہ پانچ سو کی پہلی سطروں میں اس سے پہلے والے حصے کی بات پوری ہو رہی ہے۔ حضور ا"),
        ],
        6552,
    )
    join_parts(
        "jild30-hadith-146",
        [('jild30-p547', None), ('jild30-hadith-146', None)],
        [
            (0, "end", " اپنی کتاب الامام میں خوب کلام کیا، اور اس بحث کا بقیہ حصہ اگلے صفحے پر جاری ہے۔"),
            (1, "start", "یہ صفحات اس حدیث کی بحث کا بقیہ حصہ ہیں جو پچھلے حصے سے چلی آ رہی ہے۔ اس حدیث کی"),
        ],
        6004,
    )
    join_parts(
        "jild30-irshad-33",
        [('jild30-irshad-33', None)],
        [
            (0, "end", "نبی جو کسی انسان سے پڑھے لکھے نہیں، اللہ نے خود علم دیا، انبیاء کہیں گے کہ ہم سب"),
            (1, "start", "یہ ارشاد پچھلے صفحے سے چلا آ رہا ہے؛ یہاں صرف اس کا بقیہ حصہ ہے۔ اس کی حدیث صحیح"),
        ],
        1539,
    )
    join_parts(
        "jild30-hadith-175",
        [('jild30-hadith-175', None)],
        [
            (0, "end", "ا دی، اس نے یوسف علیہ الصلوٰۃ والسلام کی قبر بتا دی۔ رفاقت کا مطلب ہے ساتھ رہنا۔"),
            (1, "start", "یہ حدیث ۱۷۵ کا بقیہ حصہ ہے جو صفحہ ۵۹۸ سے شروع ہوئی تھی: وہ بڑی بی جس نے حضرت مو"),
        ],
        11252,
    )
    print(f"after joins: {len(all_items)} items (225 concatenated)")
    # NO renames at merge for Jild 30. The duplicate-id assertion
    # runs AFTER the joins (J28 lesson: run it after the renames —
    # here there are none, so after the joins).
    assert len(all_items) == len({it["id"] for it in all_items}), (
        f"DUPLICATE IDS after joins: "
        f"{[i for i in [it['id'] for it in all_items] if [it['id'] for it in all_items].count(i) > 1]}"
    )
    print(f"after joins: {len(all_items)} items, all ids unique")
    # Absorbed ids must be gone.
    assert not any(it["id"] == "jild30-ayat-ashira" for it in all_items), f"absorbed id jild30-ayat-ashira still present"
    assert not any(it["id"] == "jild30-ayat-19-40" for it in all_items), f"absorbed id jild30-ayat-19-40 still present"
    assert not any(it["id"] == "jild30-aman-hadith-95" for it in all_items), f"absorbed id jild30-aman-hadith-95 still present"
    assert not any(it["id"] == "jild30-aman-hadith-129-start" for it in all_items), f"absorbed id jild30-aman-hadith-129-start still present"
    assert not any(it["id"] == "jild30-p547" for it in all_items), f"absorbed id jild30-p547 still present"
    # STABLE SORT by start_page, mirroring the v3 merge.
    all_items.sort(key=lambda it: it["start_page"])
    print(f"sorted by start_page: {len(all_items)} items")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    assert empty == ["jild30-hadi-al-hayran-fasl-dawwam-sawal"], f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    assert total_markers == 0, f"page markers remain in output: {total_markers}"
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-30.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-30.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
