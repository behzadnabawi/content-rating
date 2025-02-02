from django.core.management.base import BaseCommand
from content.models import Content


class Command(BaseCommand):
    help = 'Creates sample content for testing'

    def handle(self, *args, **kwargs):
        contents = [
            {
                'title': 'Table Tennis: More Than a Sport',
                'text': 'Table tennis taught me more than spin and speed. It’s about resilience, strategy, '
                        'and connecting across cultures. Coaching made me realize: mentorship is a rally that never '
                        'ends. '
            },
            {
                'title': 'Data Structures = Life Lessons',
                'text': 'Stacks teach us to handle problems one at a time. Queues remind us to be patient. Graphs? '
                        'They’re all about connections. Data structures are more than code—they’re life lessons. '
            },
            {
                'title': 'The Coaching Paradox',
                'text': 'Coaching isn’t about having all the answers. It’s about asking the right questions, '
                        'inspiring growth, and believing in potential even when it’s hidden. #Coaching #Mentorship '
            }
        ]

        for content_data in contents:
            Content.objects.create(**content_data)
            self.stdout.write(
                self.style.SUCCESS(f'Created content: {content_data["title"]}')
            )
