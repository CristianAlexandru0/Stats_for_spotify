import plotly.express as plot

def show_graph(top_7_genres,third_column):
    labels = []
    values = []
    # show only 6 genres
    for pair in top_7_genres[:6]:
        labels.append(pair[0].title())
        values.append(pair[1])

    graphic = plot.pie(names = labels, values = values, hole = 0.4, color_discrete_sequence = plot.colors.sequential.Greens_r)

    # costumize the graphic
    graphic.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=200, 
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )

    # shows the percent and name inside the graphic
    graphic.update_traces(
        textposition='inside', 
        textinfo='percent+label'

    )
    
    third_column.plotly_chart(graphic, use_container_width=True)
    return third_column
