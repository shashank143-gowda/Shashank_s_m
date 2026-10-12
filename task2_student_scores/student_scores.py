"""Task 2: fetch students' test scores from an API, compute the average, draw a bar chart.

Expected API response (JSON list):  [{"name": "Asha", "score": 78}, ...]
Set API_URL to your real API. If it cannot be reached, sample data is used.
If your API uses other field names, change NAME_KEY / SCORE_KEY below.
"""
import requests
import matplotlib
matplotlib.use('Agg')            # draw to a file; remove this line to open a window
import matplotlib.pyplot as plt

API_URL = 'https://example.com/api/students'   # replace with your real API
NAME_KEY, SCORE_KEY = 'name', 'score'

SAMPLE = [{'name': 'Asha', 'score': 78}, {'name': 'Ravi', 'score': 91},
          {'name': 'Meena', 'score': 66}, {'name': 'John', 'score': 84},
          {'name': 'Priya', 'score': 72}]


def get_students():
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f'API failed ({e}). Using sample data instead.')
        return SAMPLE


def main():
    students = get_students()
    names = [s[NAME_KEY] for s in students]
    scores = [s[SCORE_KEY] for s in students]

    average = sum(scores) / len(scores)
    print(f'Number of students: {len(scores)}')
    print(f'Average score: {average:.2f}')

    plt.figure(figsize=(8, 5))
    plt.bar(names, scores, color='steelblue')
    plt.axhline(average, color='red', linestyle='--', label=f'Average = {average:.2f}')
    plt.title('Student Test Scores')
    plt.xlabel('Student')
    plt.ylabel('Score')
    plt.legend()
    plt.tight_layout()
    plt.savefig('scores_chart.png')
    print('Chart saved as scores_chart.png')


if __name__ == '__main__':
    main()
