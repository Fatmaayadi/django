from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from events.models import EventCategory, Location, Event, UserInterest
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with Tunisian events, categories, and locations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))
        
        # Create admin user if doesn't exist
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@events.tn',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user'))
        
        # Create Tunisian organizer users
        organizers = []
        organizer_data = [
            ('amine_ben_salem', 'Amine', 'Ben Salem', 'amine@events.tn'),
            ('leila_trabelsi', 'Leila', 'Trabelsi', 'leila@events.tn'),
            ('mohamed_khelifi', 'Mohamed', 'Khelifi', 'mohamed@events.tn'),
            ('fatma_hamdi', 'Fatma', 'Hamdi', 'fatma@events.tn'),
            ('youssef_gharbi', 'Youssef', 'Gharbi', 'youssef@events.tn'),
            ('sarra_mejri', 'Sarra', 'Mejri', 'sarra@events.tn'),
        ]
        
        for username, first, last, email in organizer_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                    'is_staff': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            organizers.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(organizers)} organizers'))
        
        # Create categories
        categories_data = [
            ('Musique', 'Concerts, festivals musicaux et spectacles live'),
            ('Sport', 'Événements sportifs, compétitions et tournois'),
            ('Arts & Culture', 'Expositions, théâtre, cinéma et patrimoine'),
            ('Technologie', 'Conférences tech, startups et innovation'),
            ('Gastronomie', 'Festivals culinaires, dégustations et ateliers'),
            ('Business', 'Networking, conférences et formations professionnelles'),
            ('Éducation', 'Ateliers, formations et conférences éducatives'),
            ('Bien-être', 'Yoga, fitness, santé et développement personnel'),
            ('Famille', 'Activités familiales et événements pour enfants'),
            ('Nature', 'Randonnées, plongée et activités outdoor'),
            ('Gaming', 'Compétitions e-sport et gaming events'),
            ('Mode', 'Défilés, fashion shows et workshops mode'),
            ('Littérature', 'Salons du livre et rencontres littéraires'),
            ('Photographie', 'Expositions photo et workshops'),
            ('Danse', 'Spectacles de danse et soirées'),
        ]
        
        categories = {}
        for name, description in categories_data:
            cat, created = EventCategory.objects.get_or_create(
                name=name,
                defaults={'image': None}
            )
            categories[name] = cat
            if created:
                self.stdout.write(f'Created category: {name}')
        
        # Create Tunisian locations
        locations_data = [
            ('Cité de la Culture', 'Boulevard 9 Avril 1938, Tunis', 3000),
            ('Théâtre de l\'Opéra', 'Avenue Bourguiba, Tunis', 1200),
            ('Stade Olympique de Radès', 'Radès, Tunis', 60000),
            ('Stade Hammadi Agrebi', 'Avenue Hédi Chaker, Radès', 18000),
            ('Carthage Land', 'Avenue Habib Bourguiba, Yasmine Hammamet', 5000),
            ('La Marsa Beach', 'Corniche de La Marsa, Tunis', 8000),
            ('Hôtel Golden Tulip', 'Avenue Mohamed V, Tunis', 500),
            ('Espace Ennasr', 'Cité Ennasr, Ariana', 800),
            ('Centre Culturel Ibn Khaldoun', 'Avenue de Paris, Tunis', 600),
            ('Palais des Congrès Tunis', 'Centre Urbain Nord, Tunis', 2000),
            ('Site Archéologique Carthage', 'Carthage, Tunis', 2500),
            ('Amphithéâtre El Jem', 'El Jem, Mahdia', 5000),
            ('Medina de Tunis', 'Rue Jamaa Ezzitouna, Tunis', 1000),
            ('Port El Kantaoui', 'Port El Kantaoui, Sousse', 3000),
            ('Marina de Yasmine Hammamet', 'Yasmine Hammamet, Nabeul', 2000),
            ('Parc du Belvédère', 'Place Pasteur, Tunis', 10000),
            ('Sidi Bou Said Village', 'Sidi Bou Said, Tunis', 1500),
            ('Lac de Tunis', 'Boulevard de l\'Environnement, Tunis', 5000),
            ('Plage de Gammarth', 'Gammarth, Tunis', 6000),
            ('Dar Zaghouan', 'Avenue Farhat Hached, Tunis', 400),
            ('Hotel Sheraton Tunis', 'Avenue de la Ligue Arabe, Tunis', 800),
            ('TGM Station La Marsa', 'La Marsa, Tunis', 300),
            ('Espace El Teatro', 'Lac 2, Tunis', 1200),
            ('Club Africain Stadium', 'Rue de Marseille, Tunis', 15000),
            ('Djerba Explore Park', 'Midoun, Djerba', 2000),
        ]
        
        locations = {}
        for name, address, capacity in locations_data:
            loc, created = Location.objects.get_or_create(
                name=name,
                defaults={
                    'address': address,
                    'capacity': capacity
                }
            )
            locations[name] = loc
            if created:
                self.stdout.write(f'Created location: {name}')
        
        # Create Tunisian events
        events_data = [
            # Musique
            ('Festival International de Carthage', 'Musique', 'Site Archéologique Carthage', 45, 35, 
             'Le festival de musique le plus prestigieux de Tunisie avec des artistes arabes et internationaux de renommée mondiale.'),
            ('Jazz à Carthage', 'Musique', 'Théâtre de l\'Opéra', 38, 28, 
             'Soirée jazz exceptionnelle dans le cadre majestueux du théâtre de l\'Opéra de Tunis.'),
            ('Symphonie à la Cité', 'Musique', 'Cité de la Culture', 35, 42, 
             'Concert symphonique avec l\'Orchestre National Tunisien interprétant les grandes œuvres classiques.'),
            ('Electro Beach Festival Hammamet', 'Musique', 'Marina de Yasmine Hammamet', 55, 60, 
             'Festival de musique électronique sur la plage avec les meilleurs DJs internationaux.'),
            ('Concert Saber Rebai Live', 'Musique', 'Cité de la Culture', 42, 21, 
             'Concert exceptionnel de la star tunisienne Saber Rebai avec ses plus grands succès.'),
            ('Festival Malouf Testour', 'Musique', 'Centre Culturel Ibn Khaldoun', 25, 45, 
             'Festival de musique traditionnelle malouf célébrant le patrimoine musical tunisien.'),
            
            # Sport
            ('Derby Espérance vs Club Africain', 'Sport', 'Stade Olympique de Radès', 30, 12, 
             'Le derby tunisien tant attendu ! Vivez l\'intensité du match entre les deux géants du football tunisien.'),
            ('Marathon de Carthage', 'Sport', 'Site Archéologique Carthage', 20, 50, 
             'Marathon international à travers les sites historiques de Carthage. Parcours unique et pittoresque.'),
            ('Tournoi de Beach Volley La Marsa', 'Sport', 'La Marsa Beach', 15, 18, 
             'Tournoi de beach volley sur les plages de La Marsa. Ambiance festive garantie !'),
            ('Rallye de Tunisie Auto', 'Sport', 'Lac de Tunis', 35, 40, 
             'Étape du championnat de rallye avec les meilleurs pilotes nationaux et internationaux.'),
            ('Compétition de Natation Nationale', 'Sport', 'Hôtel Golden Tulip', 15, 25, 
             'Championnats nationaux de natation avec les nageurs élites tunisiens.'),
            
            # Arts & Culture
            ('Journées Théâtrales de Carthage', 'Arts & Culture', 'Théâtre de l\'Opéra', 28, 30, 
             'Festival international de théâtre présentant les meilleures créations contemporaines.'),
            ('Exposition Calligraphie Arabe', 'Arts & Culture', 'Cité de la Culture', 12, 15, 
             'Exposition exceptionnelle de calligraphie arabe classique et contemporaine.'),
            ('Festival du Film de Carthage', 'Arts & Culture', 'Cité de la Culture', 20, 55, 
             'Journées Cinématographiques de Carthage - le plus ancien festival de cinéma africain.'),
            ('Spectacle Son et Lumière Carthage', 'Arts & Culture', 'Site Archéologique Carthage', 32, 8, 
             'Spectacle multimédia retraçant l\'histoire glorieuse de Carthage dans un décor antique.'),
            ('Nuit des Musées Tunis', 'Arts & Culture', 'Medina de Tunis', 0, 22, 
             'Découverte nocturne des musées et galeries de la médina avec animations et concerts.'),
            
            # Technologie
            ('Tunisia Startup Summit', 'Technologie', 'Palais des Congrès Tunis', 0, 38, 
             'Le plus grand événement startup de Tunisie. Pitchs, networking et rencontres avec investisseurs.'),
            ('Hackathon 48h TechLab', 'Technologie', 'Espace Ennasr', 15, 20, 
             'Hackathon intensif pour développer des solutions tech innovantes. Prix et mentorat.'),
            ('IA & Innovation Forum', 'Technologie', 'Palais des Congrès Tunis', 25, 32, 
             'Conférence sur l\'intelligence artificielle et l\'innovation digitale en Afrique.'),
            ('Digital Marketing Conference', 'Technologie', 'Hotel Sheraton Tunis', 45, 26, 
             'Formation et conférence sur le marketing digital et les réseaux sociaux.'),
            
            # Gastronomie
            ('Festival Couscous & Gastronomie', 'Gastronomie', 'Port El Kantaoui', 18, 14, 
             'Festival célébrant le couscous tunisien et la gastronomie méditerranéenne.'),
            ('Marché Artisanal Sidi Bou Said', 'Gastronomie', 'Sidi Bou Said Village', 0, 5, 
             'Marché artisanal avec produits du terroir, pâtisseries tunisiennes et dégustations.'),
            ('Atelier Cuisine Tunisienne', 'Gastronomie', 'Dar Zaghouan', 40, 11, 
             'Cours de cuisine avec un chef tunisien pour apprendre les secrets des plats traditionnels.'),
            ('Festival de la Harissa', 'Gastronomie', 'Medina de Tunis', 10, 35, 
             'Festival dédié à la harissa tunisienne avec dégustations et ateliers culinaires.'),
            ('Soirée Dégustation Vins Tunisiens', 'Gastronomie', 'Hotel Sheraton Tunis', 50, 28, 
             'Découverte des vins tunisiens avec sommelier et accord mets & vins.'),
            
            # Business
            ('Tunisia Business Forum', 'Business', 'Palais des Congrès Tunis', 80, 33, 
             'Forum international des affaires réunissant entrepreneurs et investisseurs.'),
            ('Networking Entrepreneurs Tunis', 'Business', 'Hotel Sheraton Tunis', 20, 9, 
             'Soirée networking pour entrepreneurs et professionnels dans une ambiance conviviale.'),
            ('Conférence Leadership Féminin', 'Business', 'Cité de la Culture', 35, 24, 
             'Conférence inspirante sur le leadership féminin avec des femmes leaders tunisiennes.'),
            ('Formation Export & Commerce', 'Business', 'Palais des Congrès Tunis', 120, 40, 
             'Formation professionnelle sur l\'export et le commerce international.'),
            
            # Éducation
            ('Salon de l\'Étudiant Tunisie', 'Éducation', 'Palais des Congrès Tunis', 0, 45, 
             'Salon de l\'orientation avec universités, écoles et entreprises présentes.'),
            ('Conférence Sciences & Recherche', 'Éducation', 'Cité de la Culture', 15, 30, 
             'Conférence scientifique avec chercheurs tunisiens et internationaux.'),
            ('Atelier Coding Kids Tunis', 'Éducation', 'Espace Ennasr', 25, 12, 
             'Initiation ludique à la programmation pour enfants de 8 à 14 ans.'),
            ('Workshop Robotique', 'Éducation', 'Espace Ennasr', 35, 19, 
             'Atelier pratique de construction et programmation de robots.'),
            
            # Bien-être
            ('Yoga au Lever du Soleil', 'Bien-être', 'Plage de Gammarth', 20, 6, 
             'Session de yoga matinale sur la plage face à la Méditerranée.'),
            ('Salon Bien-être & Santé', 'Bien-être', 'Palais des Congrès Tunis', 10, 27, 
             'Salon dédié au bien-être, santé naturelle et développement personnel.'),
            ('Retraite Méditation Weekend', 'Bien-être', 'Carthage Land', 95, 48, 
             'Weekend de méditation et ressourcement dans un cadre exceptionnel.'),
            ('Marathon de Fitness Outdoor', 'Bien-être', 'Parc du Belvédère', 15, 16, 
             'Journée fitness en plein air avec cours collectifs variés.'),
            
            # Famille
            ('Carthage Land Journée Famille', 'Famille', 'Carthage Land', 28, 7, 
             'Journée famille au parc d\'attractions avec manèges et spectacles.'),
            ('Spectacle Marionnettes Enfants', 'Famille', 'Centre Culturel Ibn Khaldoun', 12, 10, 
             'Spectacle de marionnettes traditionnel tunisien pour enfants.'),
            ('Atelier Poterie Famille', 'Famille', 'Sidi Bou Said Village', 18, 13, 
             'Atelier créatif parent-enfant pour créer des poteries traditionnelles.'),
            ('Cinéma en Plein Air Gammarth', 'Famille', 'Plage de Gammarth', 0, 21, 
             'Projection de films familiaux sur la plage sous les étoiles.'),
            
            # Nature
            ('Randonnée Cap Bon', 'Nature', 'Port El Kantaoui', 15, 17, 
             'Randonnée guidée dans les montagnes du Cap Bon avec vue mer.'),
            ('Plongée Îles Kerkennah', 'Nature', 'Marina de Yasmine Hammamet', 85, 36, 
             'Excursion plongée aux îles Kerkennah pour découvrir les fonds marins.'),
            ('Observation Oiseaux Lac Ichkeul', 'Nature', 'Lac de Tunis', 12, 23, 
             'Sortie ornithologique au parc national d\'Ichkeul, site UNESCO.'),
            ('Clean-up Beach Hammamet', 'Nature', 'Marina de Yasmine Hammamet', 0, 11, 
             'Action citoyenne de nettoyage des plages de Hammamet.'),
            
            # Gaming
            ('Tunisia E-sport Championship', 'Gaming', 'Cité de la Culture', 25, 29, 
             'Championnat national d\'e-sport avec les meilleures équipes tunisiennes.'),
            ('Gaming Expo Tunis', 'Gaming', 'Palais des Congrès Tunis', 18, 37, 
             'Exposition gaming avec test de jeux, tournois et rencontres.'),
            ('LAN Party Tunis 24h', 'Gaming', 'Espace Ennasr', 20, 15, 
             'LAN party de 24h avec tournois multi-jeux et ambiance geek.'),
            ('Game Dev Meetup', 'Gaming', 'Espace El Teatro', 0, 8, 
             'Rencontre mensuelle des développeurs de jeux vidéo tunisiens.'),
            
            # Mode
            ('Tunisia Fashion Week', 'Mode', 'Cité de la Culture', 75, 44, 
             'Semaine de la mode tunisienne avec défilés de créateurs locaux et internationaux.'),
            ('Marché Vintage La Marsa', 'Mode', 'TGM Station La Marsa', 5, 4, 
             'Marché vintage et seconde main avec pièces uniques et tendances.'),
            ('Workshop Stylisme Tunisien', 'Mode', 'Centre Culturel Ibn Khaldoun', 45, 20, 
             'Atelier de stylisme explorant la mode traditionnelle et contemporaine tunisienne.'),
            ('Défilé Caftan Moderne', 'Mode', 'Hotel Sheraton Tunis', 60, 39, 
             'Défilé de caftans modernes revisitant la tradition avec créativité.'),
            
            # Littérature
            ('Salon International du Livre', 'Littérature', 'Palais des Congrès Tunis', 8, 47, 
             'Le plus grand salon du livre en Tunisie avec auteurs, éditeurs et conférences.'),
            ('Rencontre Auteur Kamel Daoud', 'Littérature', 'Centre Culturel Ibn Khaldoun', 15, 25, 
             'Rencontre littéraire avec l\'écrivain et discussion autour de ses œuvres.'),
            ('Nuit de la Poésie Arabe', 'Littérature', 'Medina de Tunis', 10, 31, 
             'Soirée poétique célébrant la poésie arabe classique et moderne.'),
            ('Club de Lecture Mensuel', 'Littérature', 'Dar Zaghouan', 0, 6, 
             'Rendez-vous mensuel des passionnés de lecture pour échanger et découvrir.'),
            
            # Photographie
            ('Expo Photo Street Tunisia', 'Photographie', 'Cité de la Culture', 10, 18, 
             'Exposition de photographie de rue capturant l\'essence de la Tunisie contemporaine.'),
            ('Workshop Photo Portrait', 'Photographie', 'Sidi Bou Said Village', 55, 22, 
             'Atelier photo portrait dans les ruelles pittoresques de Sidi Bou Said.'),
            ('Balade Photo Médina Tunis', 'Photographie', 'Medina de Tunis', 20, 9, 
             'Sortie photo guidée dans la médina avec conseils techniques.'),
            ('Concours Photo Nature', 'Photographie', 'Parc du Belvédère', 0, 34, 
             'Concours de photographie nature avec jury professionnel et prix.'),
            
            # Danse
            ('Spectacle Danse Orientale', 'Danse', 'Théâtre de l\'Opéra', 35, 41, 
             'Spectacle de danse orientale par une troupe professionnelle tunisienne.'),
            ('Soirée Salsa Latino Beach', 'Danse', 'La Marsa Beach', 20, 14, 
             'Soirée salsa sur la plage avec cours débutant et DJ latino.'),
            ('Battle Street Dance Tunisia', 'Danse', 'Espace El Teatro', 15, 26, 
             'Battle de street dance réunissant les meilleurs danseurs tunisiens.'),
            ('Stage Danse Contemporaine', 'Danse', 'Cité de la Culture', 40, 19, 
             'Stage intensif de danse contemporaine avec chorégraphe international.'),
        ]
        
        # Create events
        now = timezone.now()
        events_created = 0
        
        for title, cat_name, loc_name, price, days_offset, description in events_data:
            event_date = now + timedelta(days=days_offset)
            organizer = random.choice(organizers)
            
            event, created = Event.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'category': categories[cat_name],
                    'location': locations[loc_name],
                    'date': event_date,
                    'price': price,
                    'capacity': locations[loc_name].capacity if random.random() > 0.3 else random.randint(50, 500),
                    'created_by': organizer,
                }
            )
            if created:
                events_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {events_created} events'))
        
        # Create Tunisian test users
        test_users_data = [
            ('rania_ben_ali', 'Rania', 'Ben Ali', ['Musique', 'Arts & Culture', 'Gastronomie']),
            ('karim_jebali', 'Karim', 'Jebali', ['Sport', 'Nature', 'Bien-être']),
            ('nesrine_chemli', 'Nesrine', 'Chemli', ['Technologie', 'Business', 'Éducation']),
            ('hamza_mokni', 'Hamza', 'Mokni', ['Gaming', 'Technologie', 'Musique']),
            ('mariem_slimani', 'Mariem', 'Slimani', ['Mode', 'Arts & Culture', 'Photographie']),
            ('anis_dridi', 'Anis', 'Dridi', ['Sport', 'Gaming', 'Technologie']),
            ('ines_mahjoub', 'Ines', 'Mahjoub', ['Littérature', 'Éducation', 'Arts & Culture']),
        ]
        
        for username, first, last, interests in test_users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.tn',
                    'first_name': first,
                    'last_name': last,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                
                # Add interests
                for interest_name in interests:
                    UserInterest.objects.get_or_create(
                        user=user,
                        name=interest_name
                    )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(test_users_data)} test users with interests'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== DATABASE POPULATION COMPLETE ==='))
        self.stdout.write(f'Categories: {EventCategory.objects.count()}')
        self.stdout.write(f'Locations: {Location.objects.count()}')
        self.stdout.write(f'Events: {Event.objects.count()}')
        self.stdout.write(f'Users: {User.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\nComptes de connexion:'))
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Utilisateurs test: rania_ben_ali, karim_jebali, etc. / password123')