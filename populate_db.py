"""
Run this script once to populate the database with actor encodings.
Place actor headshot images in the actor_images/ folder before running.
Run with:  python populate_db.py
"""

import face_recognition
import cv2
import numpy
import sqlite3
import os
from database import setup_database, get_connection

ACTORS = [
    {
        "name": "Chris Evans",
        "dob": "1981-06-13",
        "nationality": "American",
        "image": "actor_images/Chris_Evans.jpg",
        "films": [
            {"title": "Captain America: The First Avenger", "year": 2011, "genre": "Action", "role": "Steve Rogers"},
            {"title": "Captain America: The Winter Soldier", "year": 2014, "genre": "Action", "role": "Steve Rogers"},
            {"title": "Avengers: Endgame",                  "year": 2019, "genre": "Action", "role": "Steve Rogers"},
            {"title": "Knives Out",                         "year": 2019, "genre": "Mystery","role": "Ransom Drysdale"},
            {"title": "The Gray Man",                       "year": 2022, "genre": "Action", "role": "Lloyd Hansen"},
            {"title": "Gifted",                             "year": 2017, "genre": "Drama",  "role": "Frank Adler"},
            {"title": "Defending Jacob",                    "year": 2020, "genre": "Drama Series", "role": "Andy Barber"},
            {"title": "Playing It Cool",                    "year": 2014, "genre": "Romance","role": "Me"},
        ]
    },
    {
        "name": "Chris Hemsworth",
        "dob": "1983-08-11",
        "nationality": "Australian",
        "image": "actor_images/Chris_Hemsworth.jpg",
        "films": [
            {"title": "Thor",                     "year": 2011, "genre": "Action",      "role": "Thor Odinson"},
            {"title": "Thor: Ragnarok",           "year": 2017, "genre": "Action",      "role": "Thor Odinson"},
            {"title": "Thor: Love and Thunder",   "year": 2022, "genre": "Action",      "role": "Thor Odinson"},
            {"title": "Avengers: Endgame",        "year": 2019, "genre": "Action",      "role": "Thor Odinson"},
            {"title": "Extraction",               "year": 2020, "genre": "Action",      "role": "Tyler Rake"},
            {"title": "Extraction 2",             "year": 2023, "genre": "Action",      "role": "Tyler Rake"},
            {"title": "Bad Times at the El Royale","year": 2018,"genre": "Thriller",    "role": "Billy Lee"},
            {"title": "Limitless",                "year": 2022, "genre": "Drama Series","role": "Himself"},
        ]
    },
    {
        "name": "Emily Blunt",
        "dob": "1983-02-23",
        "nationality": "British",
        "image": "actor_images/Emily_Blunt.jpg",
        "films": [
            {"title": "A Quiet Place",              "year": 2018, "genre": "Horror",       "role": "Evelyn Abbott"},
            {"title": "A Quiet Place Part II",      "year": 2021, "genre": "Horror",       "role": "Evelyn Abbott"},
            {"title": "Oppenheimer",                "year": 2023, "genre": "Drama",        "role": "Katherine Oppenheimer"},
            {"title": "The Devil Wears Prada",      "year": 2006, "genre": "Comedy",       "role": "Emily Charlton"},
            {"title": "Edge of Tomorrow",           "year": 2014, "genre": "Sci-Fi",       "role": "Rita Vrataski"},
            {"title": "Jungle Cruise",              "year": 2021, "genre": "Adventure",    "role": "Dr Lily Houghton"},
            {"title": "Mary Poppins Returns",       "year": 2018, "genre": "Musical",      "role": "Mary Poppins"},
            {"title": "The English",                "year": 2022, "genre": "Drama Series", "role": "Lady Cornelia Locke"},
        ]
    },
    {
        "name": "Jennifer Lawrence",
        "dob": "1990-08-15",
        "nationality": "American",
        "image": "actor_images/Jennifer_Lawrence.jpg",
        "films": [
            {"title": "The Hunger Games",                "year": 2012, "genre": "Action",       "role": "Katniss Everdeen"},
            {"title": "The Hunger Games: Catching Fire", "year": 2013, "genre": "Action",       "role": "Katniss Everdeen"},
            {"title": "Silver Linings Playbook",         "year": 2012, "genre": "Drama",        "role": "Tiffany Maxwell"},
            {"title": "X-Men: Days of Future Past",      "year": 2014, "genre": "Action",       "role": "Raven / Mystique"},
            {"title": "American Hustle",                 "year": 2013, "genre": "Crime",        "role": "Rosalyn Rosenfeld"},
            {"title": "No Hard Feelings",                "year": 2023, "genre": "Comedy",       "role": "Maddie Barker"},
            {"title": "Causeway",                        "year": 2022, "genre": "Drama",        "role": "Lynsey"},
            {"title": "Barely Famous",                   "year": 2015, "genre": "Drama Series", "role": "Herself"},
        ]
    },
    {
        "name": "Johnny Depp",
        "dob": "1963-06-09",
        "nationality": "American",
        "image": "actor_images/Johnny_Depp.jpg",
        "films": [
            {"title": "Pirates of the Caribbean: The Curse of the Black Pearl", "year": 2003, "genre": "Adventure",    "role": "Jack Sparrow"},
            {"title": "Pirates of the Caribbean: Dead Man's Chest",             "year": 2006, "genre": "Adventure",    "role": "Jack Sparrow"},
            {"title": "Edward Scissorhands",             "year": 1990, "genre": "Fantasy",      "role": "Edward Scissorhands"},
            {"title": "Charlie and the Chocolate Factory","year": 2005, "genre": "Fantasy",      "role": "Willy Wonka"},
            {"title": "Black Mass",                      "year": 2015, "genre": "Crime",        "role": "Whitey Bulger"},
            {"title": "Fantastic Beasts: The Crimes of Grindelwald", "year": 2018, "genre": "Fantasy", "role": "Gellert Grindelwald"},
            {"title": "21 Jump Street",                  "year": 1987, "genre": "Crime Series", "role": "Officer Tom Hanson"},
            {"title": "Into the Woods",                  "year": 2014, "genre": "Musical",      "role": "The Wolf"},
        ]
    },
    {
        "name": "Meryl Streep",
        "dob": "1949-06-22",
        "nationality": "American",
        "image": "actor_images/Meryl_Streep.jpg",
        "films": [
            {"title": "The Devil Wears Prada",  "year": 2006, "genre": "Comedy",       "role": "Miranda Priestly"},
            {"title": "Kramer vs. Kramer",      "year": 1979, "genre": "Drama",        "role": "Joanna Kramer"},
            {"title": "Mamma Mia!",             "year": 2008, "genre": "Musical",      "role": "Donna Sheridan"},
            {"title": "Mamma Mia! Here We Go Again", "year": 2018, "genre": "Musical", "role": "Donna Sheridan"},
            {"title": "The Iron Lady",          "year": 2011, "genre": "Drama",        "role": "Margaret Thatcher"},
            {"title": "Sophie's Choice",        "year": 1982, "genre": "Drama",        "role": "Sophie Zawistowski"},
            {"title": "Big Little Lies",        "year": 2019, "genre": "Drama Series", "role": "Mary Louise Wright"},
            {"title": "Only Murders in the Building", "year": 2023, "genre": "Crime Series", "role": "Loretta Durkin"},
        ]
    },
    {
        "name": "Michael B Jordan",
        "dob": "1987-02-09",
        "nationality": "American",
        "image": "actor_images/Michael_B_Jordan.jpg",
        "films": [
            {"title": "Black Panther",       "year": 2018, "genre": "Action",       "role": "Erik Killmonger"},
            {"title": "Creed",               "year": 2015, "genre": "Drama",        "role": "Adonis Creed"},
            {"title": "Creed II",            "year": 2018, "genre": "Drama",        "role": "Adonis Creed"},
            {"title": "Creed III",           "year": 2023, "genre": "Drama",        "role": "Adonis Creed"},
            {"title": "Fruitvale Station",   "year": 2013, "genre": "Drama",        "role": "Oscar Grant"},
            {"title": "Without Remorse",     "year": 2021, "genre": "Action",       "role": "John Kelly"},
            {"title": "Friday Night Lights", "year": 2006, "genre": "Drama Series", "role": "Vince Howard"},
            {"title": "The Wire",            "year": 2002, "genre": "Crime Series", "role": "Wallace"},
        ]
    },
    {
        "name": "Sofia Carson",
        "dob": "1993-04-10",
        "nationality": "American",
        "image": "actor_images/Sofia_Carson.jpg",
        "films": [
            {"title": "Descendants",              "year": 2015, "genre": "Fantasy",      "role": "Evie"},
            {"title": "Descendants 2",            "year": 2017, "genre": "Fantasy",      "role": "Evie"},
            {"title": "Descendants 3",            "year": 2019, "genre": "Fantasy",      "role": "Evie"},
            {"title": "Purple Hearts",            "year": 2022, "genre": "Romance",      "role": "Cassie Salazar"},
            {"title": "Feel the Beat",            "year": 2020, "genre": "Comedy",       "role": "April"},
            {"title": "The Stafford Project",     "year": 2013, "genre": "Drama",        "role": "Lily"},
            {"title": "Pretty Little Liars: The Perfectionists", "year": 2019, "genre": "Drama Series", "role": "Ava Jalali"},
            {"title": "Adventures in Babysitting","year": 2016, "genre": "Comedy",       "role": "Lola"},
        ]
    },
    {
        "name": "Tom Holland",
        "dob": "1996-06-01",
        "nationality": "British",
        "image": "actor_images/Tom_Holland.jpg",
        "films": [
            {"title": "Spider-Man: Homecoming",   "year": 2017, "genre": "Action",       "role": "Peter Parker"},
            {"title": "Spider-Man: Far From Home","year": 2019, "genre": "Action",       "role": "Peter Parker"},
            {"title": "Spider-Man: No Way Home",  "year": 2021, "genre": "Action",       "role": "Peter Parker"},
            {"title": "Avengers: Infinity War",   "year": 2018, "genre": "Action",       "role": "Peter Parker"},
            {"title": "Uncharted",                "year": 2022, "genre": "Adventure",    "role": "Nathan Drake"},
            {"title": "Cherry",                   "year": 2021, "genre": "Drama",        "role": "Cherry"},
            {"title": "The Impossible",           "year": 2012, "genre": "Drama",        "role": "Lucas Bennett"},
            {"title": "The Crowded Room",         "year": 2023, "genre": "Drama Series", "role": "Danny Sullivan"},
        ]
    },
    {
        "name": "Zendaya",
        "dob": "1996-09-01",
        "nationality": "American",
        "image": "actor_images/Zendaya.jpg",
        "films": [
            {"title": "Spider-Man: Homecoming",   "year": 2017, "genre": "Action",       "role": "MJ"},
            {"title": "Spider-Man: No Way Home",  "year": 2021, "genre": "Action",       "role": "MJ"},
            {"title": "Dune",                     "year": 2021, "genre": "Sci-Fi",       "role": "Chani"},
            {"title": "Dune: Part Two",           "year": 2024, "genre": "Sci-Fi",       "role": "Chani"},
            {"title": "The Greatest Showman",     "year": 2017, "genre": "Musical",      "role": "Anne Wheeler"},
            {"title": "Challengers",              "year": 2024, "genre": "Drama",        "role": "Tashi Duncan"},
            {"title": "Euphoria",                 "year": 2019, "genre": "Drama Series", "role": "Rue Bennett"},
            {"title": "K.C. Undercover",          "year": 2015, "genre": "Crime Series", "role": "K.C. Cooper"},
        ]
    },
    {
        "name": "Gemma Chan",
        "dob": "1982-11-29",
        "nationality": "British",
        "image": "actor_images/Gemma_Chan.jpg",
        "films": [
            {"title": "Crazy Rich Asians",        "year": 2018, "genre": "Romance",      "role": "Astrid Young Teo"},
            {"title": "Eternals",                 "year": 2021, "genre": "Action",       "role": "Sersi"},
            {"title": "Captain Marvel",           "year": 2019, "genre": "Action",       "role": "Minn-Erva"},
            {"title": "Don't Worry Darling",      "year": 2022, "genre": "Thriller",     "role": "Shelley"},
            {"title": "Rogue One",                "year": 2016, "genre": "Sci-Fi",       "role": "Bix Caleen"},
            {"title": "Mary Queen of Scots",      "year": 2018, "genre": "Drama",        "role": "Li"},
            {"title": "Humans",                   "year": 2015, "genre": "Drama Series", "role": "Anita / Mia"},
            {"title": "Sherlock",                 "year": 2014, "genre": "Crime Series", "role": "Soo Lin Yao"},
            {"title": "Fresh Meat",               "year": 2011, "genre": "Drama Series", "role": "Mei Lin"},
            {"title": "Secret Diary of a Call Girl", "year": 2008, "genre": "Drama Series", "role": "Vanessa"},
        ]
    },
    {
        "name": "Henry Golding",
        "dob": "1987-02-05",
        "nationality": "British-Malaysian",
        "image": "actor_images/Henry_Golding.jpg",
        "films": [
            {"title": "Crazy Rich Asians",             "year": 2018, "genre": "Romance",  "role": "Nick Young"},
            {"title": "Snake Eyes",                    "year": 2021, "genre": "Action",   "role": "Snake Eyes"},
            {"title": "A Simple Favor",                "year": 2018, "genre": "Thriller", "role": "Sean Townsend"},
            {"title": "Last Christmas",                "year": 2019, "genre": "Romance",  "role": "Tom"},
            {"title": "The Gentlemen",                 "year": 2019, "genre": "Crime",    "role": "Dry Eye"},
            {"title": "Guy Ritchie's The Covenant",    "year": 2023, "genre": "Action",   "role": "Ahmed"},
            {"title": "Monsoon",                       "year": 2020, "genre": "Drama",    "role": "Kit"},
            {"title": "The MME Experience",            "year": 2022, "genre": "Drama Series", "role": "Host"},
            {"title": "Bang Bang Baby",                "year": 2022, "genre": "Crime Series", "role": "Guest"},
        ]
    },
    {
        "name": "Simu Liu",
        "dob": "1989-04-19",
        "nationality": "Canadian-Chinese",
        "image": "actor_images/Simu_Liu.jpg",
        "films": [
            {"title": "Shang-Chi and the Legend of the Ten Rings", "year": 2021, "genre": "Action",  "role": "Shang-Chi"},
            {"title": "Barbie",                   "year": 2023, "genre": "Comedy",       "role": "Ken"},
            {"title": "Arthur the King",          "year": 2024, "genre": "Adventure",    "role": "Leo"},
            {"title": "One True Loves",           "year": 2023, "genre": "Romance",      "role": "Sam"},
            {"title": "Poor Things",              "year": 2023, "genre": "Drama",        "role": "Guest"},
            {"title": "Kim's Convenience",        "year": 2016, "genre": "Drama Series", "role": "Jung Kim"},
            {"title": "Taken",                    "year": 2017, "genre": "Action Series","role": "Han Li"},
            {"title": "Blood and Water",          "year": 2021, "genre": "Crime Series", "role": "Guest"},
            {"title": "Awkwafina is Nora from Queens", "year": 2020, "genre": "Drama Series", "role": "Guest"},
        ]
    },
    {
        "name": "Michelle Yeoh",
        "dob": "1962-08-06",
        "nationality": "Malaysian",
        "image": "actor_images/Michelle_Yeoh.jpg",
        "films": [
            {"title": "Everything Everywhere All at Once", "year": 2022, "genre": "Sci-Fi",   "role": "Evelyn Wang"},
            {"title": "Crazy Rich Asians",        "year": 2018, "genre": "Romance",      "role": "Eleanor Young"},
            {"title": "Crouching Tiger Hidden Dragon", "year": 2000, "genre": "Action",  "role": "Yu Shu Lien"},
            {"title": "Tomorrow Never Dies",      "year": 1997, "genre": "Action",       "role": "Wai Lin"},
            {"title": "Shang-Chi and the Legend of the Ten Rings", "year": 2021, "genre": "Action", "role": "Ying Nan"},
            {"title": "Shang-Chi and the Legend of the Ten Rings 2", "year": 2025, "genre": "Action", "role": "Ying Nan"},
            {"title": "Guardians of the Galaxy Vol 3", "year": 2023, "genre": "Action",  "role": "Aleta Ogord"},
            {"title": "The Mummy: Tomb of the Dragon Emperor", "year": 2008, "genre": "Action", "role": "Zi Yuan"},
            {"title": "Star Trek: Discovery",     "year": 2017, "genre": "Drama Series", "role": "Captain Philippa Georgiou"},
            {"title": "The Witcher: Blood Origin","year": 2022, "genre": "Drama Series", "role": "Scian"},
            {"title": "American Born Chinese",    "year": 2023, "genre": "Drama Series", "role": "Guanyin"},
        ]
    },
    {
        "name": "Sandra Oh",
        "dob": "1971-07-20",
        "nationality": "Canadian",
        "image": "actor_images/Sandra_Oh.jpg",
        "films": [
            {"title": "Sideways",                 "year": 2004, "genre": "Comedy",       "role": "Stephanie"},
            {"title": "Last Night in Soho",       "year": 2021, "genre": "Thriller",     "role": "Miss Collins"},
            {"title": "Bird Box",                 "year": 2018, "genre": "Horror",       "role": "Olympia"},
            {"title": "Turning Red",              "year": 2022, "genre": "Comedy",       "role": "Ming Lee"},
            {"title": "The Chair",                "year": 2021, "genre": "Drama Series", "role": "Ji-Yoon Kim"},
            {"title": "Killing Eve",              "year": 2018, "genre": "Crime Series", "role": "Eve Polastri"},
            {"title": "Grey's Anatomy",           "year": 2005, "genre": "Drama Series", "role": "Cristina Yang"},
            {"title": "Arlo the Alligator Boy",   "year": 2021, "genre": "Comedy",       "role": "Edmée"},
            {"title": "The Princess Diaries",     "year": 2001, "genre": "Comedy",       "role": "Vice Principal Gupta"},
            {"title": "Shrill",                   "year": 2019, "genre": "Drama Series", "role": "Guest"},
        ]
    },
    {
        "name": "Sandra Bullock",
        "dob": "1964-07-26",
        "nationality": "American",
        "image": "actor_images/Sandra_Bullock.jpg",
        "films": [
            {"title": "Speed",                    "year": 1994, "genre": "Action",       "role": "Annie Porter"},
            {"title": "Miss Congeniality",        "year": 2000, "genre": "Comedy",       "role": "Gracie Hart"},
            {"title": "Miss Congeniality 2",      "year": 2005, "genre": "Comedy",       "role": "Gracie Hart"},
            {"title": "Gravity",                  "year": 2013, "genre": "Sci-Fi",       "role": "Dr Ryan Stone"},
            {"title": "Bird Box",                 "year": 2018, "genre": "Horror",       "role": "Malorie"},
            {"title": "The Blind Side",           "year": 2009, "genre": "Drama",        "role": "Leigh Anne Tuohy"},
            {"title": "The Lost City",            "year": 2022, "genre": "Comedy",       "role": "Loretta Sage"},
            {"title": "Ocean's Eight",            "year": 2018, "genre": "Crime",        "role": "Debbie Ocean"},
            {"title": "The Proposal",             "year": 2009, "genre": "Romance",      "role": "Margaret Tate"},
            {"title": "Bullet Train",             "year": 2022, "genre": "Action",       "role": "Lady Bug"},
            {"title": "Bird Box Barcelona",       "year": 2023, "genre": "Horror",       "role": "Malorie"},
        ]
    },
    {
        "name": "Tom Cruise",
        "dob": "1962-07-03",
        "nationality": "American",
        "image": "actor_images/Tom_Cruise.jpg",
        "films": [
            {"title": "Top Gun",                  "year": 1986, "genre": "Action",       "role": "Maverick"},
            {"title": "Top Gun: Maverick",        "year": 2022, "genre": "Action",       "role": "Maverick"},
            {"title": "Mission: Impossible",      "year": 1996, "genre": "Action",       "role": "Ethan Hunt"},
            {"title": "Mission: Impossible II",   "year": 2000, "genre": "Action",       "role": "Ethan Hunt"},
            {"title": "Mission: Impossible III",  "year": 2006, "genre": "Action",       "role": "Ethan Hunt"},
            {"title": "Mission: Impossible – Fallout", "year": 2018, "genre": "Action",  "role": "Ethan Hunt"},
            {"title": "Mission: Impossible – Dead Reckoning", "year": 2023, "genre": "Action", "role": "Ethan Hunt"},
            {"title": "Jerry Maguire",            "year": 1996, "genre": "Drama",        "role": "Jerry Maguire"},
            {"title": "A Few Good Men",           "year": 1992, "genre": "Drama",        "role": "Lt. Daniel Kaffee"},
            {"title": "Oblivion",                 "year": 2013, "genre": "Sci-Fi",       "role": "Jack Harper"},
            {"title": "Edge of Tomorrow",         "year": 2014, "genre": "Sci-Fi",       "role": "Major William Cage"},
            {"title": "The Mummy",                "year": 2017, "genre": "Action",       "role": "Nick Morton"},
        ]
    },
    {
        "name": "Matt Damon",
        "dob": "1970-10-08",
        "nationality": "American",
        "image": "actor_images/Matt_Damon.jpg",
        "films": [
            {"title": "Good Will Hunting",        "year": 1997, "genre": "Drama",        "role": "Will Hunting"},
            {"title": "The Martian",              "year": 2015, "genre": "Sci-Fi",       "role": "Mark Watney"},
            {"title": "Jason Bourne",             "year": 2016, "genre": "Action",       "role": "Jason Bourne"},
            {"title": "The Bourne Identity",      "year": 2002, "genre": "Action",       "role": "Jason Bourne"},
            {"title": "The Bourne Supremacy",     "year": 2004, "genre": "Action",       "role": "Jason Bourne"},
            {"title": "The Bourne Ultimatum",     "year": 2007, "genre": "Action",       "role": "Jason Bourne"},
            {"title": "Interstellar",             "year": 2014, "genre": "Sci-Fi",       "role": "Dr Mann"},
            {"title": "The Departed",             "year": 2006, "genre": "Crime",        "role": "Colin Sullivan"},
            {"title": "Oppenheimer",              "year": 2023, "genre": "Drama",        "role": "General Leslie Groves"},
            {"title": "Air",                      "year": 2023, "genre": "Drama",        "role": "Phil Knight"},
            {"title": "Ocean's Eleven",           "year": 2001, "genre": "Crime",        "role": "Linus Caldwell"},
            {"title": "Ocean's Twelve",           "year": 2004, "genre": "Crime",        "role": "Linus Caldwell"},
        ]
    },
    {
        "name": "Anne Hathaway",
        "dob": "1982-11-12",
        "nationality": "American",
        "image": "actor_images/Anne_Hathaway.jpg",
        "films": [
            {"title": "The Devil Wears Prada",    "year": 2006, "genre": "Comedy",       "role": "Andy Sachs"},
            {"title": "The Dark Knight Rises",    "year": 2012, "genre": "Action",       "role": "Selina Kyle"},
            {"title": "Les Misérables",           "year": 2012, "genre": "Musical",      "role": "Fantine"},
            {"title": "Interstellar",             "year": 2014, "genre": "Sci-Fi",       "role": "Dr Amelia Brand"},
            {"title": "Ocean's Eight",            "year": 2018, "genre": "Crime",        "role": "Daphne Kluger"},
            {"title": "The Princess Diaries",     "year": 2001, "genre": "Comedy",       "role": "Mia Thermopolis"},
            {"title": "The Princess Diaries 2",   "year": 2004, "genre": "Comedy",       "role": "Mia Thermopolis"},
            {"title": "Brokeback Mountain",       "year": 2005, "genre": "Drama",        "role": "Alma Beers"},
            {"title": "The Witches",              "year": 2020, "genre": "Fantasy",      "role": "The Grand High Witch"},
            {"title": "Armageddon Time",          "year": 2022, "genre": "Drama",        "role": "Esther Graff"},
            {"title": "WeCrashed",                "year": 2022, "genre": "Drama Series", "role": "Rebekah Neumann"},
            {"title": "Modern Love",              "year": 2019, "genre": "Drama Series", "role": "Lexi"},
        ]
    },
]

def get_or_insert_film(cursor, film):
    """Insert a film if it doesn't exist, return its ID."""
    cursor.execute("SELECT film_id FROM films WHERE title = ? AND year = ?", (film["title"], film["year"]))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "INSERT INTO films (title, year, genre) VALUES (?, ?, ?)",
        (film["title"], film["year"], film["genre"])
    )
    return cursor.lastrowid

def populate():
    setup_database()
    conn = get_connection()
    cursor = conn.cursor()

    for actor in ACTORS:
        print(f"Processing {actor['name']}...")

        if not os.path.exists(actor["image"]):
            print(f"  ⚠ Image not found: {actor['image']} — skipping")
            continue

        image = face_recognition.load_image_file(actor["image"])
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            print(f"  ⚠ No face found in {actor['image']} — skipping")
            continue

        encoding = encodings[0]
        encoding_blob = encoding.tobytes()

        cursor.execute(
            "INSERT INTO actors (name, dob, nationality, face_encoding) VALUES (?, ?, ?, ?)",
            (actor["name"], actor["dob"], actor["nationality"], encoding_blob)
        )
        actor_id = cursor.lastrowid

        for film in actor["films"]:
            film_id = get_or_insert_film(cursor, film)
            cursor.execute(
                "INSERT OR IGNORE INTO actor_films (actor_id, film_id, role) VALUES (?, ?, ?)",
                (actor_id, film_id, film["role"])
            )

        print(f"  ✓ Added {actor['name']} with {len(actor['films'])} films and series")

    conn.commit()
    conn.close()
    print("\nDatabase populated successfully.")

if __name__ == "__main__":
    populate() 