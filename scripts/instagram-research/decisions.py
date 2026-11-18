#!/usr/bin/env python3
"""Hand adjudication of the venues whose own site links more than one account.

Officiality is already established for every handle here: it was found as a link
on the venue's own official site (stage 1). What is decided below is *which* of
those official accounts belongs to this venue, and whether it is the branch's own
account or the brand/operator's shared one.

Rule applied, deliberately conservative:
  - exactly one candidate clearly corresponds to this venue or branch  -> VERIFIED
  - only a brand/operator-wide account exists for this venue           -> VERIFIED, account_type "brand"
  - two or more remain plausible, or none corresponds                  -> AMBIGUOUS, every candidate kept
No handle is chosen on name similarity alone, and none is invented.
"""

# id -> (handle or None, account_type, note)
DECISIONS = {
    "L031": ("maidensshop_jimbocho", "store", "Jimbocho branch account; the others are the brand, the women's line and a separate store."),
    "L058": ("fuglenhanegikoen", "store", "Hanegikoen branch account among the chain's eight branch accounts."),
    "L067": ("bondicoffeesandwiches", "store", "Main account; hiroo / nakameguro / komazawa are other branches."),
    "L073": ("inishie_waguriyamontblancstyle", "store", "Matches this venue; kuriya_farmer is the farm side of the business."),
    "L074": ("theobroma_japan", "brand", "No account for the main shop alone; brand account. Others are the cacao store, the gelateria and the chef's personal account."),
    "L101": ("tokyodome1988_", "store", "The dome itself; tokyodomecity_official covers the surrounding complex."),
    "L102": ("mufg_stadium", "store", "The stadium's own account; themusicstadium_official is the event brand."),
    "L117": (None, "", "The monument has no account of its own. The site links two Yasukuni Shrine accounts and neither is the statue's - left ambiguous rather than attributing the shrine's account to a monument."),
    "L134": (None, "", "The shrine's own site links two accounts (yasukuni.official / yasukunijinja) and does not say which is current."),
    "L136": (None, "", "Museum inside Yasukuni; its page links the shrine's two accounts, neither specific to the museum."),
    "L175": ("spincoastermusicbarebisu", "store", "Ebisu branch account."),
    "L180": ("ristorante_aso", "store", "The restaurant's own account; hiramatsu_restaurant is the operating group."),
    "L184": ("aoyamagrand", "store", "The hotel's own account; the other two are its restaurants."),
    "L215": (None, "", "The museum's site links only tnm_ir_en / tnm_ir_kr (language-specific information accounts); the main museum account is not linked from it."),
    "L223": ("kandamyoujin", "store", "The shrine's own account; the others are its bridal service and the EDOCCO hall."),
    "L227": ("marunouchi_maruzen", "store", "The Marunouchi store's account; the others are its stationery, Japanese-book and gallery floors, and the honto service."),
    "L235": ("spincoastermusicbar", "brand", "No Shinjuku branch account is linked; the linked branch accounts are Ebisu and Kagurazaka, so only the brand account applies."),
    "L265": (None, "", "Restaurant inside THE AOYAMA GRAND HOTEL. The hotel site links the hotel and two sibling restaurants, none of them this one."),
    "L329": (None, "", "Branch accounts linked are Kasukabe, Himonya and Shibuya; none names Toritsu-Daigaku, and guessing the nearest is not evidence."),
    "L335": ("wolfgangssteakhouse_marunouchi", "store", "Marunouchi branch account among the chain's branch accounts."),
    "L340": ("bltsteak_roppongi", "store", "Roppongi branch account; queens.steakburger is a sibling brand."),
    "L396": (None, "", "The temple's site links two accounts (nishi.hongwanji / nishi_hongwanji) without saying which is current."),
    "L415": ("tsuruya.yoshinobu_honten", "store", "Main-shop account among the brand's several accounts."),
    "L431": (None, "", "The tower's site links two accounts (tsutenkaku_official / tsutenkakutower_official) without distinguishing them."),
    "L463": ("kobebeef_mouriya_honten", "store", "Main-shop account; kobebeef_mouriya is the brand."),
    "L475": (None, "", "Linked accounts are the station branch and a separate standing-sushi shop; no account for this shop is identifiable."),
    "L500": ("hokudai_bg", "store", "The botanical garden's own account; hokkaidounivpr is the university's PR account."),
    "L501": (None, "", "Only akarenga_chousha_1888 is plausible, and the page also links unrelated accounts; not confirmable from this page alone."),
    "L518": ("hakubahappoone", "brand", "Operator account for the Happo-one hot springs; this bath has no account of its own."),
    "L519": ("hakubahappoone", "brand", "Operator account for the Happo-one hot springs; this bath has no account of its own."),
}


# Publisher / platform accounts that appear as page furniture on directory and
# media sites. They are never a venue's account.
PUBLISHER_HANDLES = {
    "hamoni_jp", "san_tatsu", "rurubuandmore", "rurubuplus", "timeouttokyo_jp",
    "aumo_odekake", "admatic_official", "tvtokyo_pr", "bs7ch_pr", "hitosara_official",
    "macaroni_news", "sauna_ikitai", "mapple_net", "tabelog_official", "retty_official",
    "hotpepper_gourmet", "gnavi_official", "jalan_net", "walkerplus", "ozmall_official",
    "makuake_official", "gendai_media", "note_official",
}

# Venues reached through a directory page in stage 2. Same conservative rule as
# above: a handle is taken only when it clearly corresponds to this venue.
STAGE2_DECISIONS = {
    "調和": ("chowa.kitasenju", "store", "Matches the venue and its neighbourhood; the other accounts are sibling shops of the same owner."),
    "Quindi": ("quindi_tokyo", "store", "The restaurant's own account."),
    "ホルン": (None, "", "The only Instagram link on the page reached was rurubuplus, the publisher's own account."),
    "パークハイアット 東京": ("parkhyatttokyo", "store", "The hotel's own account."),
    "明治神宮": (None, "", "Accounts reached are Meiji Kinenkan and the shrine's support association, neither of them the shrine's own account."),
    "かっぱ橋道具街": (None, "", "Only accounts of individual shops in the street were reached, not the shopping street's own."),
    "The Top.": (None, "", "Only the hotel's and its sibling restaurants' accounts were reached, none of them this bar's."),
    "all day place shibuya": ("alldayplace_shibuya", "store", "The hotel's own account among the operator's list."),
    "炭火串焼 ふく": ("sumibikushiyaki_fuku", "store", "The restaurant's own account."),
    "Soul Music BAR Ali-Ollie!!!!": ("bar_aliollie", "store", "The bar's own account."),
    "酒場それがし": ("soregashi_official", "store", "The bar's own account."),
    "上野動物園": ("tokyo_zoogram", "brand", "Account of the Tokyo Zoological Park Society, which runs this zoo and others; no zoo-only account was reached."),
    "THE GREAT BURGER": (None, "", "Accounts reached belong to other businesses; none corresponds to this restaurant."),
    "御所南 かまた": ("kamata_gosyominami", "store", "The restaurant's own account."),
    "大阪城": (None, "", "Two park accounts were reached (osaka_castle_park / osakacastlepark.odekake) and the page does not say which is official."),
    "天神橋筋商店街": (None, "", "Only accounts of individual shops in the arcade were reached, not the arcade's own."),
    "新梅田食道街": ("shinumedasyokudougai", "store", "The arcade's own account."),
    "柳助": ("ryuusuke_otaru", "store", "The restaurant's own account."),
    "炭火焼肉 深山": (None, "", "The account reached (fullmarks_official) belongs to an unrelated business."),
}
