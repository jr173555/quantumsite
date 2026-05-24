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
        self.coordinates = np.array(coordinates)
        self.edges = np.array(edges)
        self.height_lims = (
            np.min(coordinates, axis=0)[2],
            np.max(coordinates, axis=0)[2],
        )
        self.boxes = []
        for idx, (x, y, z) in enumerate(coordinates):
            self.boxes.append(Box(idx, x, y, z))

    def _draw_edge(self, figure: go.Figure, edge_idx: int):
        idx1, idx2 = self.edges[edge_idx]
        x0, y0 = self.coordinates[idx1][:2]
        x1, y1 = self.coordinates[idx2][:2]
        if y0 == y1:
            y0, y1 = y0, y1 + 1
            if x1 < x0:
                idx1, idx2 = idx2, idx1
            x0, x1 = x1, x1
            self.boxes[idx1].borders["right"] = True
            self.boxes[idx2].borders["left"] = True
        elif x0 == x1:
            x0, x1 = x0, x1 + 1
            if y1 < y0:
                idx1, idx2 = idx2, idx1
            y0, y1 = y1, y1
            self.boxes[idx1].borders["up"] = True
            self.boxes[idx2].borders["down"] = True
        else:
            raise ValueError(f"Invalid edge between ({x0}, {y0}) and ({x1}, {y1})")
        figure.add_shape(
            type="line",
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            line=dict(color="black", width=2, dash="dot"),
        )

    def _draw_missing_edges(self, figure: go.Figure):
        for box in self.boxes:
            x, y = box.x, box.y
            edge_coords = {
                "up": (x, y + 1, x + 1, y + 1),
                "down": (x, y, x + 1, y),
                "left": (x, y, x, y + 1),
                "right": (x + 1, y, x + 1, y + 1),
            }
            for direction, (x0, y0, x1, y1) in edge_coords.items():
                if not box.borders[direction]:
                    figure.add_shape(
                        type="line",
                        x0=x0,
                        y0=y0,
                        x1=x1,
                        y1=y1,
                        line=dict(color="black", width=2),
                    )

    def _reset_borders(self):
        for box in self.boxes:
            box._reset_borders()

    def draw(self):
        figure = go.Figure()

        for box in self.boxes:
            box.draw_box(figure, self.height_lims)

        for edge_idx in range(len(self.edges)):
            self._draw_edge(figure, edge_idx)

        self._draw_missing_edges(figure)

        figure.update_layout(
            title="Quantum Site Visualization",
            xaxis_title="X Coordinate",
            yaxis_title="Y Coordinate",
            xaxis=dict(constrain="domain", showgrid=False),
            yaxis=dict(scaleanchor="x", scaleratio=1, showgrid=False),
            showlegend=False,
        )
        figure.show()
        self._reset_borders()


class Box:

    def __init__(self, idx: int, x: float, y: float, z: float):
        self.idx: int = idx
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.borders = {"up": False, "down": False, "left": False, "right": False}

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

        # Draw the square in data coordinates so it scales correctly with zoom.
        figure.add_shape(
            type="rect",
            x0=self.x,
            y0=self.y,
            x1=self.x + 1,
            y1=self.y + 1,
            fillcolor=color,
            line=dict(color=color),
        )

        # Invisible scatter point at the centre keeps hover text working.
        figure.add_trace(
            go.Scatter(
                x=[self.x + 0.5],
                y=[self.y + 0.5],
                mode="markers",
                marker=dict(size=1, color=color, opacity=0),
                hovertext=text,
                hoverinfo="text",
                name="Node",
                showlegend=True,
            ),
        )

    def _reset_borders(self):
        self.borders = {"up": False, "down": False, "left": False, "right": False}
