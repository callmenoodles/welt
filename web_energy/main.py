# TODO: Organize "measure" module
import os
from web_energy import charts
from web_energy.utils import globals



def main():
    tool = 'scaphandre'
    category = 'informational'
    chart = 'qq'

    df = charts.get_dataframe(tool, category)

    if chart == 'bar':
        graph = charts.gen_barchart(df)
    elif chart == 'qq':
        graph = charts.gen_qq(df, category)
    else:
        graph = charts.gen_histogram(df)

    graph.savefig(os.path.join(globals.PROJECT_ROOT, 'out', 'graphs', f'{tool}-{chart}-{category}.png'))
    graph.show()


if __name__ == '__main__':
    main()