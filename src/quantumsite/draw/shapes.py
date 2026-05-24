import numpy as np
import plotly.graph_objects as go
import plotly.express as px

cmap = px.colors.sequential.Agsunset


class Canvas:

    def __init__(
        self,
        coordinates: list[tuple[float, float, float]],
        edges: list[tuple[int, int]],
    ):
        self.coordinates: list[tuple[float, float, float]] = coordinates
        self.edges: list[tuple[int, int]] = edges
        self.height_lims = (
            np.min(coordinates, axis=0)[2],
            np.max(coordinates, axis=0)[2],
        )

    def draw(self):
        figure = go.Figure()

        for idx, (x, y, z) in enumerate(self.coordinates):
            box = Box(idx, x, y, z)
            box.draw_box(figure, self.height_lims)

        # for idx1, idx2 in self.edges:
        #    x1, y1, _ = self.coordinates[idx1]
        #    x2, y2, _ = self.coordinates[idx2]
        #    figure.add_trace(
        #        go.Scatter(
        #            x=[x1, x2],
        #            y=[y1, y2],
        #            mode="lines",
        #            line=dict(color="lightgray", width=1),
        #            showlegend=False,
        #        ),
        #    )

        figure.update_layout(
            title="Quantum Site Visualization",
            xaxis_title="X Coordinate",
            yaxis_title="Y Coordinate",
            xaxis=dict(constrain="domain", showgrid=False),
            yaxis=dict(scaleanchor="x", scaleratio=1, showgrid=False),
            showlegend=True,
        )
        figure.show()


class Box:

    def __init__(self, idx: int, x: float, y: float, z: float, size: float = 10):
        self.idx: int = idx
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.size: float = size

    def draw_box(
        self, figure: go.Figure, height_lims: None | tuple[float, float] = None
    ):
        if height_lims is not None and (height_lims[0] < height_lims[1]):
            min_height, max_height = height_lims
            relative_z = (self.z - min_height) / (max_height - min_height)
            color = cmap[int(relative_z * (len(cmap) - 1))]
            text = f"Index: {self.idx}<br>Height: {self.z:.2f}"
        else:
            color = "lightgray"
            text = f"Index: {self.idx}"

        marker = {"size": 15, "color": color, "symbol": "square"}
        figure.add_trace(
            go.Scatter(
                x=[self.x],
                y=[self.y],
                mode="markers",
                marker=marker,
                hovertext=text,
                name="Node",
                showlegend=True,
            ),
        )
