import os
from web_energy import charts
from web_energy.utils import globals


def main():
    tool = 'codecarbon'
    chart = 'hist'

    for category in globals.CATEGORIES:
        df = charts.get_dataframe(tool, category)

        if chart == 'bar':
            graph = charts.gen_barchart(df)
        elif chart == 'qq':
            graph = charts.gen_qq(df, category)
        else:
            graph = charts.gen_histogram(df, is_labeled=True)

        graph.savefig(os.path.join(globals.PROJECT_ROOT, 'out', 'graphs', f'{tool}-{chart}-{category}.png'))


if __name__ == '__main__':
    main()