"""places_data.py - the places added for the district-wise Destinations view.

Each row is one place:
    (key, title, dzongkhag, subtitle, stay, nu_per_person, description, [(highlight, one line) x3])

* key         short unique id (letters, digits, dashes). It is what favourites / bucket list store.
* nu_per_person is a PLACEHOLDER price in Ngultrum - confirm every one before you take bookings
  (see places_to_confirm.csv for the full list).
* PHOTOS: no image is listed here on purpose. Drop a file called  images/<key>.jpg  (or .jpeg /
  .png / .webp) into the images folder and the card + detail page pick it up on the next start.
  Until then the place shows a neutral "photo coming soon" card.

The twelve original places (Tiger's Nest, Punakha Dzong ...) stay in catalog.py with their own
photos and wording.
"""

NEW_PLACES = [
    # ------------------------------------------------------------------ PARO
    ("rinpung-dzong", "Rinpung Dzong", "Paro", "Fortress of Jewels", "1 day", "2,500",
     "Rinpung Dzong, built in 1645 by Zhabdrung Ngawang Namgyal, rises above the Paro valley as both monastery and "
     "district office. Its whitewashed walls and carved wooden galleries are among the best of western Bhutan.",
     [("Nemi Zam bridge", "Cross the traditional covered wooden bridge that leads to the dzong."),
      ("Courtyards and temples", "Walk the courtyards where monks and district offices share the building."),
      ("Paro Tshechu", "The dzong's courtyard hosts Paro's yearly festival of masked dances.")]),
    ("kyichu-lhakhang", "Kyichu Lhakhang", "Paro", "Ancient Temple", "1 day", "2,000",
     "Kyichu Lhakhang is one of Bhutan's oldest temples, said to date from the 7th century and to have been founded "
     "by the Tibetan king Songtsen Gampo. It is a calm, atmospheric stop close to Paro town.",
     [("7th-century origins", "Visit a temple that is among the oldest in the Himalayas."),
      ("Quiet courtyard", "Spend a few peaceful minutes among prayer wheels and old trees."),
      ("Later temple", "See the newer temple added beside the original shrine.")]),
    ("chele-la", "Chele La Pass", "Paro", "High Mountain Pass", "1 day", "2,500",
     "At about 3,988 m, Chele La is one of Bhutan's highest motorable passes, on the road between Paro and Haa. "
     "Strings of prayer flags frame wide mountain views on a clear day.",
     [("Prayer flags", "Add your own flag to the thousands already flying at the pass."),
      ("Mountain views", "On a clear day, look out towards Jomolhari."),
      ("Paro to Haa road", "Drive one of the most scenic mountain roads in the west.")]),
    ("drukgyal-dzong", "Drukgyal Dzong", "Paro", "Fortress Ruins", "1 day", "2,000",
     "Drukgyal Dzong was built in 1649 to mark a victory over Tibetan invasions and was destroyed by fire in 1951. "
     "Its ruined towers stand at the head of the valley with Mount Jomolhari behind them on clear days.",
     [("Fortress ruins", "Explore the surviving walls and towers of the old dzong."),
      ("Mountain backdrop", "Look for Jomolhari rising behind the ruins on a clear day."),
      ("Valley setting", "Enjoy the quiet farmland at the top of the Paro valley.")]),
    ("national-museum", "National Museum of Bhutan", "Paro", "Ta Dzong", "1 day", "2,000",
     "The National Museum is housed in Ta Dzong, a round watchtower above Rinpung Dzong that has served as the "
     "national museum since 1968. It is a good first introduction to Bhutanese art and history.",
     [("Watchtower building", "Explore the circular tower that once guarded Rinpung Dzong."),
      ("Art and artefacts", "See thangka paintings, masks, textiles and religious objects."),
      ("Valley views", "Look down over Paro Dzong and the valley from the hillside.")]),

    # ------------------------------------------------------------------ THIMPHU
    ("memorial-chorten", "National Memorial Chorten", "Thimphu", "Daily Devotion", "1 day", "2,000",
     "Built in 1974 in memory of the Third King, Jigme Dorji Wangchuck, the Memorial Chorten is one of the most "
     "visited religious sites in Thimphu. Locals walk around it all day, spinning prayer wheels.",
     [("Daily kora", "Join Thimphu residents walking clockwise around the chorten."),
      ("White stupa and golden spire", "Admire the landmark that anchors the city centre."),
      ("Shrines inside", "Look at the painted shrines and sacred images within.")]),
    ("motithang-takin", "Motithang Takin Preserve", "Thimphu", "Meet the National Animal", "1 day", "2,000",
     "The takin is Bhutan's national animal, an unusual mix of goat and antelope. The preserve above Thimphu lets "
     "you see these animals up close in a forested setting.",
     [("Takin viewing", "See Bhutan's national animal in a natural enclosure."),
      ("Forest paths", "Walk short trails through the hillside forest."),
      ("The legend", "Hear the story of how the takin came to be.")]),
    ("folk-heritage-museum", "Folk Heritage Museum", "Thimphu", "Rural Life Up Close", "1 day", "2,000",
     "A traditional three-storey farmhouse of rammed earth and timber is set up as a museum of rural Bhutanese life. "
     "It shows how families lived, cooked and farmed in the villages.",
     [("Traditional farmhouse", "Walk through the rooms of a full-size village home."),
      ("Everyday objects", "See the tools, utensils and furnishings of rural life."),
      ("Village traditions", "Learn how households and seasons shaped daily routines.")]),
    ("changangkha-lhakhang", "Changangkha Lhakhang", "Thimphu", "Temple Above the City", "1 day", "2,000",
     "Founded in the 12th century, Changangkha Lhakhang sits on a ridge above Thimphu. Families bring newborn "
     "children here to receive a blessing and a name.",
     [("City views", "Look out over Thimphu valley from the temple courtyard."),
      ("Blessings for children", "See a tradition still very much alive."),
      ("Prayer wheels", "Spin the wheels that line the temple walls.")]),
    ("cheri-monastery", "Cheri Monastery", "Thimphu", "Mountain Retreat", "1 day", "2,500",
     "Founded in 1620 by Zhabdrung Ngawang Namgyal, Cheri Monastery is reached by a footbridge and a steady uphill "
     "walk north of Thimphu. It is a monastic retreat in a forested valley.",
     [("Footbridge and climb", "Cross the river and follow the path up through the forest."),
      ("Zhabdrung's retreat", "Visit a monastery tied to the founder of Bhutan."),
      ("Quiet setting", "Enjoy a calm, forested valley far from the city.")]),

    # ------------------------------------------------------------------ PUNAKHA
    ("chimi-lhakhang", "Chimi Lhakhang", "Punakha", "Fertility Temple", "1 day", "2,500",
     "Chimi Lhakhang is dedicated to Drukpa Kunley, the 'Divine Madman', and is famous across Bhutan as a place of "
     "blessing for couples hoping for children. A walk through rice fields leads to the temple.",
     [("Rice-field walk", "Follow a village path through the fields to the temple."),
      ("The Divine Madman", "Hear the stories of Drukpa Kunley and his unconventional teaching."),
      ("Fertility blessing", "Receive a blessing, a tradition many visitors seek out.")]),
    ("khamsum-yulley", "Khamsum Yulley Namgyal Chorten", "Punakha", "Hilltop Chorten", "1 day", "2,500",
     "Built by Queen Ashi Tshering Yangdon Wangchuck, this tall chorten stands on a ridge above the Mo Chhu. "
     "The walk to it crosses a suspension bridge and winds through paddy fields.",
     [("Paddy-field hike", "Walk up through terraced fields to the ridge."),
      ("Painted interior", "Look at the detailed murals inside the chorten."),
      ("Valley views", "See the Punakha valley and the rivers below.")]),
    ("punakha-suspension-bridge", "Punakha Suspension Bridge", "Punakha", "Walk Above the River", "1 day", "2,000",
     "One of Bhutan's longest suspension bridges stretches over the Pho Chhu close to Punakha Dzong. Crossing it, "
     "hung with prayer flags, is a short and memorable walk.",
     [("River crossing", "Walk the full length of the bridge above the Pho Chhu."),
      ("Prayer flags", "Cross beneath strings of flags blowing in the wind."),
      ("Dzong views", "Look back at Punakha Dzong from the river.")]),
    ("punakha-rafting", "Mo Chhu River Rafting", "Punakha", "River Adventure", "1 day", "3,000",
     "Punakha's rivers offer some of Bhutan's best rafting, with a calm, scenic run past farms and the dzong. "
     "It suits first-time rafters as well as families.",
     [("Easy to moderate rapids", "Enjoy a lively run that beginners can handle."),
      ("Dzong from the water", "See Punakha Dzong from an unusual angle."),
      ("Riverside scenery", "Pass farmland, forest and villages on the banks.")]),

    # ------------------------------------------------------------------ BUMTHANG
    ("jambay-lhakhang", "Jambay Lhakhang", "Bumthang", "Seventh-Century Temple", "1 day", "2,500",
     "Jambay Lhakhang is said to have been founded in the 7th century by Songtsen Gampo, one of 108 temples built "
     "in a single day to pin down a demoness. Its autumn festival is among the best known in Bhutan.",
     [("Ancient temple", "Visit one of the oldest sacred sites in the country."),
      ("Maitreya shrine", "See the central image of the future Buddha."),
      ("Jambay Lhakhang Drup", "Come in autumn for the festival of masked dances and fire rites.")]),
    ("tamshing-lhakhang", "Tamshing Lhakhang", "Bumthang", "Pema Lingpa's Temple", "1 day", "2,500",
     "Tamshing Lhakhang was founded in 1501 by the treasure-revealer Pema Lingpa. It keeps some of the oldest "
     "wall paintings in Bhutan.",
     [("Founded in 1501", "Step inside a temple of the 16th century."),
      ("Old wall paintings", "Look at the original murals that cover the walls."),
      ("Pema Lingpa's chain-mail", "Learn about the heavy iron coat kept at the temple.")]),
    ("mebar-tsho", "Mebar Tsho", "Bumthang", "The Burning Lake", "1 day", "2,500",
     "Mebar Tsho, the 'Burning Lake', is a sacred pool in a gorge of the Tang river where Pema Lingpa is said to "
     "have retrieved hidden treasures. Pilgrims float butter lamps on its waters.",
     [("The legend", "Hear the story of the treasure-revealer and his leap into the lake."),
      ("Butter lamps", "Join pilgrims who float small lamps on the water."),
      ("Gorge setting", "Walk down to the pool through a quiet river gorge.")]),
    ("ura-valley", "Ura Valley", "Bumthang", "Highland Village", "1–2 days", "3,000",
     "Ura is the highest of Bumthang's valleys, a cluster of tightly grouped houses surrounded by pasture and "
     "pine forest. It feels very different from the rest of the region.",
     [("Village lanes", "Walk the stone-paved lanes between traditional houses."),
      ("Ura Lhakhang", "Visit the village temple at the heart of the valley."),
      ("Highland scenery", "See open pastures and high mountain views.")]),
    ("ugyen-choling", "Ugyen Choling Palace", "Bumthang", "Heritage Manor", "1–2 days", "3,000",
     "Ugyen Choling is a historic manor in the remote Tang valley, now a museum of rural life and local history. "
     "The road to it passes some of the most traditional villages in Bumthang.",
     [("Manor architecture", "Look at the timber and stone building and its inner courtyard."),
      ("Museum rooms", "See displays on the household life of the old manor."),
      ("Tang valley", "Drive through a quiet side valley rarely visited by groups.")]),

    # ------------------------------------------------------------------ WANGDUE PHODRANG
    ("gangtey-monastery", "Gangtey Monastery", "Wangdue Phodrang", "Monastery of the Valley", "1 day", "2,500",
     "Gangtey Monastery stands on a hill above the Phobjikha valley and is the main Nyingma monastery of the area, "
     "founded in the early 17th century. Black-necked cranes circle it each winter.",
     [("Valley views", "Look over the whole Phobjikha valley from the monastery hill."),
      ("Prayer hall", "Step into the large prayer hall with its painted columns."),
      ("Cranes in winter", "Watch the cranes make their traditional turns around the monastery.")]),
    ("gangtey-nature-trail", "Gangtey Nature Trail", "Wangdue Phodrang", "Valley Walk", "1 day", "2,000",
     "A gentle trail leads down from Gangtey Monastery across the floor of the Phobjikha valley to the village of "
     "Semchubara. It is an easy walk through pine forest and farmland.",
     [("Forest path", "Walk under pine and rhododendron through the hillside."),
      ("Village stop", "Pass farms and houses on the valley floor."),
      ("Prayer flags", "Follow strings of flags across the open meadow.")]),
    ("black-necked-crane-centre", "Black-Necked Crane Information Centre", "Wangdue Phodrang", "Crane Watching",
     "1 day", "2,000",
     "The Black-Necked Crane Information Centre in Phobjikha explains why rare cranes winter here from Tibet. "
     "Telescopes let you watch them on the marsh.",
     [("Exhibitions", "Learn about the cranes and their journey across the Himalayas."),
      ("Telescopes", "Look at the birds on the valley marsh."),
      ("Winter visitors", "Come between late autumn and early spring to see the cranes.")]),
    ("rinchengang", "Rinchengang Village", "Wangdue Phodrang", "Village of Stonemasons", "1 day", "2,000",
     "Rinchengang is a hillside village near Wangdue whose houses are packed closely together. Its people are known "
     "for their skill as stonemasons, who helped build many of Bhutan's dzongs.",
     [("Stone houses", "Walk between traditional homes built tightly on the slope."),
      ("Craft heritage", "Learn about the villagers' work as stonemasons."),
      ("Hillside views", "Look out over the valley and the river below.")]),

    # ------------------------------------------------------------------ TRONGSA
    ("tower-of-trongsa", "Tower of Trongsa", "Trongsa", "Royal Heritage Museum", "1 day", "3,000",
     "Built as a watchtower in 1652 above Trongsa Dzong, the tower has been a museum of the Bhutanese monarchy since "
     "2008. It holds eleven galleries and two working temples.",
     [("Eleven galleries", "Follow the story of the royal family and the nation."),
      ("The Raven Crown", "See the Raven Crown, a symbol of the Bhutanese monarchy."),
      ("Working temples", "Step into temples still used for prayer.")]),
    ("chendebji-chorten", "Chendebji Chorten", "Trongsa", "Roadside Stupa", "1 day", "2,000",
     "Chendebji Chorten is a whitewashed stupa built in the 18th century in the style of Boudhanath in Nepal. It "
     "stands beside the highway in a quiet green valley below Pele La.",
     [("Nepalese-style stupa", "See the painted eyes and gold details of the chorten."),
      ("Highway stop", "A classic pause on the road between Wangdue and Trongsa."),
      ("Mountain valley", "Enjoy the stream and fields around the stupa.")]),
    ("kuenga-rabten", "Kuenga Rabten Palace", "Trongsa", "Winter Palace", "1 day", "2,500",
     "Built in 1929, Kuenga Rabten was the winter residence of the Second King and now houses monks. "
     "It sits about 23 km south of Trongsa on a quiet road.",
     [("Palace architecture", "Look at the buildings and courtyards of the old palace."),
      ("Monastic life", "See the quiet routine of the monks who live here."),
      ("Southern road", "Drive down into warmer, greener country.")]),

    # ------------------------------------------------------------------ HAA
    ("haa-white-black-temples", "White and Black Temples", "Haa", "Twin Temples", "1 day", "2,500",
     "Lhakhang Karpo and Lhakhang Nagpo, the White and the Black Temple, stand a short distance apart at the "
     "southern end of the valley. They are the oldest and best-known temples in Haa.",
     [("Lhakhang Karpo", "Visit the White Temple, where the Haa Tshechu is held."),
      ("Lhakhang Nagpo", "Walk to the Black Temple, a short stroll away."),
      ("Haa Tshechu", "Come in autumn for the festival's masked dances.")]),
    ("juneydrak", "Juneydrak Hermitage", "Haa", "Cliff Hermitage", "1 day", "2,500",
     "Juneydrak is a cliff-side hermitage above Katsho village, reached by a 40-minute to one-hour climb. It holds "
     "a footprint associated with the saint Machig Labdrön.",
     [("Cliff climb", "Hike up a forest path to the hermitage."),
      ("Sacred footprint", "See the imprint linked to Machig Labdrön."),
      ("Katsho village", "Walk through the village at the foot of the cliff.")]),

    # ------------------------------------------------------------------ GASA
    ("gasa-tshachu", "Gasa Tshachu", "Gasa", "Healing Hot Springs", "1–2 days", "3,000",
     "The hot springs at Gasa are among the best known in Bhutan, visited for their reputed healing properties. "
     "Pilgrims and travellers soak in stone baths beside the river.",
     [("Hot-spring baths", "Soak in mineral water after a long road."),
      ("River setting", "Relax beside the Mo Chhu in a forested gorge."),
      ("Healing tradition", "Learn why people have visited for generations.")]),
    ("laya-village", "Laya Village", "Gasa", "Highland Culture", "4–5 days", "5,000",
     "Laya is a high-altitude settlement in the far north of Bhutan, home to the Layap people. It is usually "
     "reached on foot and is known for its distinctive dress and culture.",
     [("Layap culture", "Meet a highland people with their own traditions."),
      ("Conical hats", "See the traditional dress, including woven bamboo hats worn by women."),
      ("Mountain trek", "Reach the village on a trek through high Himalayan scenery.")]),

    # ------------------------------------------------------------------ MONGAR
    ("drametse-monastery", "Drametse Monastery", "Mongar", "Dance of the Drums", "1 day", "2,500",
     "Founded in 1511, Drametse is one of the most important Nyingma monasteries in eastern Bhutan. Its Drametse "
     "Ngacham, the dance of the drums, is recognised by UNESCO.",
     [("UNESCO dance", "Learn about the masked drum dance listed as world heritage."),
      ("Eastern monastery", "Visit a major Nyingma monastery in the east."),
      ("Hilltop setting", "Enjoy long views from its ridge.")]),
    ("thrumshingla", "Thrumshingla National Park", "Mongar", "Cloud-Forest Wilderness", "2–3 days", "3,000",
     "Thrumshingla National Park covers a large area of forest in central and eastern Bhutan. The highway crosses "
     "the Thrumshing La pass above 3,700 m between Bumthang and Mongar.",
     [("Mountain pass", "Cross one of the highest road passes in the east."),
      ("Cloud forest", "See rhododendron, fir and mossy forest from the road."),
      ("Birdlife", "Look for pheasants and other species on a forest walk.")]),

    # ------------------------------------------------------------------ TRASHIGANG
    ("rangjung-woesel", "Rangjung Woesel Choling", "Trashigang", "Monastic Community", "1 day", "2,500",
     "Founded in 1989 east of Trashigang town, this Nyingma monastery has grown into a community of more than 300 "
     "monks and nuns.",
     [("Monks and nuns", "See a large and lively monastic community."),
      ("Prayer hall", "Step into the main temple with its painted images."),
      ("Hilltop views", "Look out over the east from the monastery.")]),
    ("merak-sakteng", "Merak and Sakteng", "Trashigang", "Land of the Brokpa", "4–5 days", "4,500",
     "Merak and Sakteng are high villages of the Brokpa, semi-nomadic herders with their own dress and customs. "
     "The visit takes several days and a rough road now reaches Merak.",
     [("Brokpa culture", "Meet herders with a way of life unlike the rest of Bhutan."),
      ("Highland pastures", "Walk across yak-grazing meadows and forests."),
      ("The migoi legend", "Hear the stories of the yeti that Sakteng is known for.")]),

    # ------------------------------------------------------------------ TSIRANG
    ("damphu-town", "Damphu Town", "Tsirang", "Southern Hill Town", "1 day", "2,000",
     "Damphu is the district centre of Tsirang, sitting at about 1,570 m. It has a single temple with a Buddhist "
     "door on one side and a Hindu door on the other.",
     [("Shared temple", "See a place of worship that serves two faiths."),
      ("Hill climate", "Enjoy a milder, warmer climate than the high valleys."),
      ("Local life", "Walk through the town and its market streets.")]),
    ("tsirang-dzong", "Tsirang Dzong", "Tsirang", "District Dzong", "1 day", "2,000",
     "Tsirang Dzong in Damphu is the administrative and monastic centre of the district. The annual district "
     "tshechu is held here.",
     [("The dzong", "Visit the district's main administrative and monastic centre."),
      ("District tshechu", "Come for the yearly festival and its rituals."),
      ("Monastic body", "See the Tsirang Namgyel Chholing monastic community.")]),

    # ------------------------------------------------------------------ SAMTSE
    ("samtse-town", "Samtse Town", "Samtse", "Gateway to the South", "1 day", "2,000",
     "Samtse is the district centre, on a plain at about 380 m close to the West Bengal border. A Buddhist "
     "monastery, a stupa and a Hindu temple stand within a few hundred metres of each other.",
     [("Local markets", "Browse the shops and cafés of a border town."),
      ("Shared faiths", "See Buddhist and Hindu sites side by side."),
      ("Warm lowlands", "Experience Bhutan at low altitude.")]),
    ("shivalaya-mandir", "Shivalaya Mandir", "Samtse", "Hindu Temple", "1 day", "2,000",
     "Shivalaya Mandir is a Hindu temple dedicated to Lord Shiva, completed in 2015 and built on royal command. "
     "It is carved from sandstone and holds statues of Shiva and other deities in sandstone and marble.",
     [("Carved sandstone", "Look at the detailed stonework of the temple."),
      ("Shiva statues", "See the marble and sandstone images inside."),
      ("A royal project", "Learn how the temple was built on royal command.")]),
    ("sidhok-khorlo-chorten", "Sidhok Khorlo Chorten", "Samtse", "Marble Stupa", "1 day", "2,000",
     "Sidhok Khorlo Chorten is a 30-foot white marble stupa completed in 2015, next to Samtse Dzong at a well-known "
     "crossroad.",
     [("Marble stupa", "See the tall white chorten at the town crossroad."),
      ("Beside the dzong", "Visit both the stupa and the dzong in one stop."),
      ("Town landmark", "A quiet place to pause and reflect.")]),
    ("dorokha", "Dorokha", "Samtse", "Cool Hills of the North", "2–3 days", "3,000",
     "Dorokha is the cooler, hillier northern part of Samtse, with mountain scenery and several ethnic "
     "communities living in villages.",
     [("Hill villages", "Walk between farms and villages in the hills."),
      ("Cooler air", "Escape the heat of the plains."),
      ("Mixed communities", "Meet people from several ethnic groups.")]),

    # ------------------------------------------------------------------ CHHUKHA
    ("phuentsholing", "Phuentsholing and Bhutan Gate", "Chhukha", "The Southern Gateway", "1 day", "2,000",
     "Phuentsholing, on the border with West Bengal, is the main road gateway into Bhutan. The ceremonial Bhutan "
     "Gate marks the crossing.",
     [("Bhutan Gate", "See the painted gate that welcomes visitors into the kingdom."),
      ("Border bazaar", "Wander the busy shops of a border town."),
      ("The road north", "Start the climb from the plains into the mountains.")]),
    ("zangtho-pelri-phuentsholing", "Zangtho Pelri Lhakhang", "Chhukha", "Celestial Abode", "1 day", "2,000",
     "The Zangtho Pelri Lhakhang in Phuentsholing is a colourful temple built as a copy of Guru Rinpoche's "
     "celestial abode.",
     [("Painted temple", "See the bright colours and detailed paintings."),
      ("Guru Rinpoche's abode", "Learn about the heavenly palace the temple represents."),
      ("Town centre stop", "A short visit close to the border gate.")]),
    ("kharbandi-goemba", "Kharbandi Goemba", "Chhukha", "Monastery Above the Plains", "1 day", "2,000",
     "Kharbandi Goemba is a hillside monastery above Phuentsholing, built in 1967 by Ashi Phuntsho Choden, the "
     "Queen Grandmother of Bhutan.",
     [("Hilltop setting", "Climb to a monastery above the town."),
      ("Plains views", "Look out across the southern plains."),
      ("Temple shrines", "Visit the small temples at the heart of the complex.")]),

    # ------------------------------------------------------------------ DAGANA
    ("daga-dzong", "Daga Dzong", "Dagana", "Ridge-Top Dzong", "1–2 days", "2,500",
     "Daga Trashi Yangtse Dzong was built in 1651 on a ridge above the valley. It houses the district "
     "administration and a monastic body, and hosts the annual tshechu in the eleventh Bhutanese month.",
     [("Ridge-top dzong", "See a 17th-century fortress above the valley."),
      ("Annual tshechu", "Come for five days of masked dances to honour Guru Rinpoche."),
      ("Village views", "Look over farmland and terraces.")]),
    ("tseza-village", "Tseza Village", "Dagana", "Village Homestays", "1–2 days", "2,500",
     "Tseza is a working village in the gewog that holds Dagana town. Visitors can stay in homestays, and "
     "descendants of the Daga Penlop still live here.",
     [("Homestay", "Stay with a family and eat home-cooked food."),
      ("Farm life", "Join in the daily work of a farming village."),
      ("Penlop heritage", "Meet families linked to the old Daga Penlop.")]),

    # ------------------------------------------------------------------ LHUENTSE
    ("lhuentse-dzong", "Lhuentse Dzong", "Lhuentse", "Dzong Above the River", "1–2 days", "3,000",
     "Lhuentse Dzong stands on a ridge above the Kuri Chhu. It began as a meditation centre in 1554 and was built up "
     "into a dzong in 1665.",
     [("River gorge views", "Look down on the Kuri Chhu from the dzong."),
      ("A 1554 beginning", "Learn how a meditation centre became a fortress."),
      ("Remote east", "Reach one of Bhutan's least-visited districts.")]),
    ("takila-guru-statue", "Takila Guru Statue", "Lhuentse", "Giant Guru Rinpoche", "1–2 days", "3,000",
     "At 154 feet (46.9 m), the Guru Rinpoche statue at Takila is the largest in Bhutan, begun in 2008 and "
     "consecrated in 2015.",
     [("Bhutan's largest Guru statue", "See a statue nearly 47 m tall."),
      ("Pilgrimage site", "Visit a place of growing importance for pilgrims."),
      ("Eastern scenery", "Take in the high ridges around the site.")]),
    ("khoma-village", "Khoma Village", "Lhuentse", "Home of Kishuthara", "2–3 days", "3,500",
     "Khoma is the village where some of Bhutan's finest kishuthara silk is woven on backstrap looms. Eleven "
     "certified homestays offer home cooking and a hot stone bath.",
     [("Kishuthara weaving", "Watch weavers make one of Bhutan's most prized textiles."),
      ("Village homestay", "Stay with a family in a certified homestay."),
      ("Hot stone bath", "Try a traditional bath after the day's walking.")]),
    ("dungkar-naktshang", "Dungkar Naktshang", "Lhuentse", "Royal Birthplace", "1–2 days", "3,000",
     "Dungkar Naktshang, in Kurtoe gewog, is the birthplace of Jigme Namgyel, the father of Bhutan's first King. "
     "The old house is a place of royal heritage.",
     [("Royal heritage", "Visit the birthplace of the father of the first King."),
      ("Kurtoe valley", "Travel through the ancestral land of the royal family."),
      ("Remote village", "See rural life far from the main tourist routes.")]),

    # ------------------------------------------------------------------ PEMAGATSHEL
    ("pemagatshel-dzong", "Pemagatshel Dzong", "Pemagatshel", "A New Dzong", "1–2 days", "2,500",
     "Druk Migyur Dechen Dzong at Denchi was built between 2012 and 2023 and consecrated in September 2023. It is "
     "now the administrative and monastic centre of the district.",
     [("New architecture", "See a dzong built in the traditional way in recent years."),
      ("District centre", "Visit the seat of the district administration and monks."),
      ("Hill views", "Look across the hills of the south-east.")]),
    ("yongla-goenpa", "Yongla Goenpa", "Pemagatshel", "Ridge-Top Monastery", "1–2 days", "2,500",
     "Yongla Goenpa is an 18th-century monastery on a ridge at about 2,480 m, rebuilt after the 2009 earthquake. "
     "A large ritual, a drubchen, is held there each September.",
     [("18th-century monastery", "Visit an old temple rebuilt with care."),
      ("Drubchen ritual", "Come in September for a multi-day ritual."),
      ("Ridge views", "Look out from the ridge at about 2,480 m.")]),
    ("thongsa-weavers", "Thongsa Cotton Weavers", "Pemagatshel", "Handwoven Cotton", "1 day", "2,000",
     "At Kamthangma in Thongsa, women grow, spin, dye and weave their own cotton. Visitors can watch the work and "
     "buy cloth at the centre.",
     [("Growing to weaving", "See every step from cotton plant to finished cloth."),
      ("Local women's craft", "Watch weavers at their looms."),
      ("Buy handwoven cloth", "Take home a piece made by the people who wove it.")]),

    # ------------------------------------------------------------------ SAMDRUP JONGKHAR
    ("sj-dzong", "Samdrup Jongkhar Dzong", "Samdrup Jongkhar", "Eastern Dzong", "1 day", "2,000",
     "Samdrup Jongkhar Dzong is a recently built dzong that houses the district administrator's office, at the "
     "eastern gateway to Bhutan.",
     [("Modern dzong", "See a dzong built in the traditional style."),
      ("District centre", "Visit the district administrator's seat."),
      ("Border town setting", "Start or end an east-Bhutan journey here.")]),
    ("sj-zangdo-pelri", "Zangdo Pelri Lhakhang", "Samdrup Jongkhar", "Celestial Abode", "1 day", "2,000",
     "A three-storey temple in the middle of town, named after the celestial abode of Guru Rinpoche.",
     [("Three-storey temple", "Walk through the levels of the lhakhang."),
      ("Town centre", "Visit a landmark right in the middle of town."),
      ("Guru Rinpoche's abode", "Learn about the heavenly palace it represents.")]),
    ("sj-town", "Samdrup Jongkhar Town", "Samdrup Jongkhar", "The Eastern Gateway", "1–2 days", "2,000",
     "Samdrup Jongkhar is the main entry to Bhutan from Assam in the east. It is a lively town where the "
     "lowlands meet the hills.",
     [("Border crossing", "Arrive in Bhutan through the eastern gate."),
      ("Town life", "Walk through the markets and streets."),
      ("Start of the east road", "Begin the long road up to Trashigang.")]),

    # ------------------------------------------------------------------ SARPANG
    ("gelephu-town", "Gelephu Town", "Sarpang", "Southern Border Town", "1 day", "2,000",
     "Gelephu is the main town of Sarpang, a warm border town at about 220 m on the southern plains.",
     [("Border bazaar", "Visit the shops and markets of the south."),
      ("Southern warmth", "Feel the lowland climate of the plains."),
      ("Gateway to the wild", "Use the town as a base for the southern national parks.")]),
    ("gelephu-hot-spring", "Gelephu Hot Spring", "Sarpang", "Seven Ponds", "1 day", "2,500",
     "The hot spring north of Gelephu has seven ponds, with men and women bathing at different times. "
     "It is busiest in January.",
     [("Seven ponds", "Soak in several pools of warm water."),
      ("Alternating times", "Follow the traditional schedule for men and women."),
      ("Winter visit", "Come in the cold season, when the spring is most popular.")]),

    # ------------------------------------------------------------------ ZHEMGANG
    ("royal-manas", "Royal Manas National Park", "Zhemgang", "Bhutan's Oldest Park", "3–4 days", "4,500",
     "Royal Manas is Bhutan's oldest protected area, running from about 108 m to 2,600 m across Sarpang, Zhemgang "
     "and Pemagatshel. Visitors enter from Panbang.",
     [("Jungle wildlife", "Look for tigers, elephants and rare birds in the subtropical forest."),
      ("Manas river", "Explore the river that gives the park its name."),
      ("Panbang entry", "Approach the park by the road from Gomphu.")]),
    ("buli-tsho", "Buli Tsho", "Zhemgang", "Sacred Lake", "1–2 days", "3,000",
     "Buli Tsho is a sacred lake of about two hectares in the forest south of Buli village. It is believed to be "
     "the home of Tshomen Kuntu Zangmo and is closed to visitors for about three months each autumn.",
     [("Sacred lake", "Visit a lake that local people hold in deep respect."),
      ("Forest walk", "Reach the shore through quiet woodland."),
      ("Seasonal closure", "Plan around the autumn closure.")]),
    ("twin-waterfall", "Twin Waterfall", "Zhemgang", "Roadside Falls", "1 day", "2,000",
     "Two streams fall side by side about 7 km from Panbang on the Gomphu–Panbang highway. The falls are known "
     "locally as Lelang.",
     [("Two streams", "See two waterfalls drop beside each other."),
      ("Roadside stop", "An easy stop on the road to Panbang."),
      ("Subtropical forest", "Look at the greenery that surrounds the falls.")]),
    ("berti-valley", "Berti Valley", "Zhemgang", "Heron Valley", "1–2 days", "3,000",
     "Berti is a valley near Tingtibi that is protected for the white-bellied heron. A community-run eco lodge of "
     "riverside cabins was built there by the district.",
     [("White-bellied heron", "Look out for one of the world's rarest birds."),
      ("Eco lodge", "Stay in a community-run riverside cabin."),
      ("River walks", "Walk along the water in a quiet forest valley.")]),

    # ------------------------------------------------------------------ TRASHIYANGTSE
    ("chorten-kora", "Chorten Kora", "Trashiyangtse", "Boudhanath of the East", "1 day", "2,500",
     "Chorten Kora is a large whitewashed stupa built in the 18th century in the style of Boudhanath in Nepal. "
     "Its yearly kora festival draws pilgrims from far around.",
     [("Nepalese-style stupa", "See the painted eyes and golden spire."),
      ("Kora festival", "Come for the yearly gathering of pilgrims."),
      ("River setting", "Walk beside the stream that flows past the chorten.")]),
    ("bumdeling", "Bumdeling Wildlife Sanctuary", "Trashiyangtse", "Winter Cranes", "2–3 days", "3,500",
     "Bumdeling Wildlife Sanctuary in the north-east is a winter home for black-necked cranes. It has forests, "
     "rivers and high pastures.",
     [("Black-necked cranes", "Come in winter to see the cranes arrive."),
      ("Forest walks", "Walk through rich mountain forest."),
      ("North-east wilds", "Visit a remote protected area.")]),
    ("trashiyangtse-dzong", "Trashiyangtse Dzong", "Trashiyangtse", "District Dzong", "1 day", "2,000",
     "Trashiyangtse Dzong is the district's administrative and monastic centre, in a valley known for its wooden "
     "crafts.",
     [("The dzong", "Visit the centre of local administration and worship."),
      ("Valley setting", "Look across a quiet eastern valley."),
      ("Wooden crafts", "Learn about the district's woodworking tradition.")]),
    ("zorig-chusum-ty", "Institute for Zorig Chusum", "Trashiyangtse", "Traditional Arts School", "1 day", "2,000",
     "The Institute for Zorig Chusum in Trashiyangtse is a school of Bhutan's traditional arts. Visitors can watch "
     "students at work in the studios.",
     [("Thirteen arts", "Learn about Bhutan's traditional arts and crafts."),
      ("Student studios", "Watch young artists painting, carving and sewing."),
      ("Local crafts", "Buy a small piece made by the students.")]),
]
