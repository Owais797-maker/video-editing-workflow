# Customer sticker / card (owner, 2026-11-22)

Owner's reference: `Video Edits/Reference/customer-sticker/ref.jpg` (cartoon shopkeeper on a warm textured
background with big bubbly "AUR MERE JAISI SERVICE" text). Use it for customer feedback / trust videos:
the customer's photo as a comic-style cut-out + a big funny/proud line + the customer's name.

Make one:
    python3 tools/posts/customer_sticker.py --photo "<photo>" --crop "x0,y0,x1,y1" --name "<Customer Sahab>" \
        --line "BHAROSA" --line "HO TO AISA!" --urdu "<short Urdu line>" [--tag "KHYBER TRADERS"] [--bg "#C8552E"]
Outputs `Export/customer-stickers/<name>-card.jpg` (9:16 4K post/status) and `<name>-sticker.png`
(transparent, white sticker border, for `overlays` in edit.json: pop it in next to the customer when he is named).

Look: Luckiest Guy caps (white, thick dark-brown outline + hard drop shadow), Urdu line in Lalezar yellow with
the same outline, warm brick/orange background, photo smoothed + posterized + ink lines (a painted look, not a
real AI cartoon), white name pill with a hard shadow, optional small yellow tag. Ideas for lines (owner's voice):
"BHAROSA HO TO AISA!", "REPEAT CUSTOMER", "RESULT DEKH KE AAYE", "KARACHI SE KHANPUR TAK".
Never copy the reference character itself; always the owner's real customer, with his permission.
