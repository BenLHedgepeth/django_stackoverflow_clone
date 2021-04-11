
from django.test import TestCase
from django.urls import reverse

class TestTopQuestionsPageBadQueryString(TestCase):
    '''Verify that when a "tab" query string argument doesn\'t
    match of any sort filters that the default is "interesting"'''
    pass

    # @classmethod
    # def setUpTestData(cls):
    #     cls.url = f"{reverse('mainpage')}/?tab=none"
    #     anchor = f'<a href={cls.url}>Interesting</a>'
    #     cls.button = f"<button class='current_sort'>{anchor}</button>"
    #
    # def test_top_questions_url_query_string_filter(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "top_questions.html")
    #     self.assertContains(response, self.button, html=True)
