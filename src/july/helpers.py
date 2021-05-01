import calendar
import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import ArrayLike
from typing import List, Tuple, Any, Optional
from datetime import date


def date_grid(
    dates: List[date], data: List[Any], flip: bool, dtype: str = "float64"
) -> ArrayLike:
    # Array with columns (iso year, iso week number, iso weekday).
    iso_dates = np.array([day.isocalendar() for day in dates])
    # Unique weeks, as defined by the tuple (iso year, iso week).
    unique_weeks = sorted(list(set([tuple(row) for row in iso_dates[:, :2]])))

    # Get dict that maps week tuple to week index in grid.
    weeknum2idx = {week: i for i, week in enumerate(unique_weeks)}
    week_coords = np.array([weeknum2idx[tuple(week)] for week in iso_dates[:, :2]])
    day_coords = iso_dates[:, 2] - 1

    # Define shape of grid.
    n_weeks = len(unique_weeks)
    n_days = 7

    # Create grid and fill with data.
    grid = np.empty((n_weeks, n_days), dtype=dtype)
    grid = np.nan * grid if dtype == "float64" else grid
    grid[week_coords, day_coords] = data

    if flip:
        return grid.T

    return grid


def cal_heatmap(
    cal: ArrayLike,
    dates,
    flip: bool,
    cmap: str = "Greens",
    colorbar: bool = False,
    date_label: bool = False,
    weekday_label: bool = True,
    month_label: bool = False,
    year_label: bool = False,
    ax: Optional[Tuple[int]] = None,
):
    if not ax:
        figsize = (10, 5) if flip else (5, 10)
        fig, ax = plt.subplots(figsize=figsize, dpi=100)

    pc = ax.pcolormesh(cal, edgecolors="white", linewidth=0.25, cmap=cmap)
    ax.invert_yaxis()
    ax.set_aspect("equal")

    if colorbar:
        bbox = ax.get_position()
        # Specify location and dimensions: [left, bottom, width, height].
        cax = fig.add_axes([bbox.x1 + 0.015, bbox.y0, 0.015, bbox.height])
        cbar = plt.colorbar(pc, cax=cax)
        cbar.ax.tick_params(size=0)

    if date_label:
        add_date_label(ax, dates, flip)
    if weekday_label:
        add_weekday_label(ax, flip)
    if month_label:
        add_month_label(ax, dates, flip)
    if year_label:
        add_year_label(ax, dates, flip)

    ax.tick_params(axis="both", which="both", length=0)

    return ax


def add_date_label(ax, dates: List[date], flip: bool) -> None:
    days = [day.day for day in dates]
    day_grid = date_grid(dates, days, flip)

    for i, j in np.ndindex(day_grid.shape):
        try:
            ax.text(j + 0.5, i + 0.5, int(date_grid[i, j]), ha="center", va="center")
        except ValueError:
            # If date_grid[i, j] is nan.
            pass


def add_weekday_label(ax, flip: bool) -> None:
    if flip:
        ax.tick_params(axis="y", which="major", pad=8)
        ax.set_yticks([x + 0.5 for x in range(0, 7)])
        ax.set_yticklabels(
            calendar.weekheader(width=1).split(" "), fontname="monospace"
        )
    else:
        ax.tick_params(axis="x", which="major", pad=4)
        ax.set_xticks([x + 0.5 for x in range(0, 7)])
        ax.set_xticklabels(
            calendar.weekheader(width=1).split(" "), fontname="monospace"
        )
        ax.xaxis.tick_top()


def add_month_label(ax, dates: List[date], flip: bool) -> None:
    month_years = [(day.year, day.month) for day in dates]
    month_years_str = list(map(str, month_years))
    month_year_grid = date_grid(dates, month_years_str, flip, dtype="object")

    unique_month_years = sorted(set(month_years))

    month_locs = {}
    for month in unique_month_years:
        # Get 'avg' x, y coordinates of elements in grid equal to month_year.
        yy, xx = np.nonzero(month_year_grid == str(month))
        month_locs[month] = (xx.max() + xx.min() if flip else yy.max() + yy.min()) / 2

    # Get month label for each unique month_year.
    month_labels = [calendar.month_abbr[x[1]] for x in month_locs.keys()]

    if flip:
        ax.set_xticks([*month_locs.values()])
        ax.set_xticklabels(month_labels, fontsize=14, fontname="monospace")
    else:
        ax.set_yticks([*month_locs.values()])
        ax.set_yticklabels(month_labels, fontsize=14, fontname="monospace", rotation=90)


def add_year_label(ax, dates, flip):
    years = [day.year for day in dates]
    year_grid = date_grid(dates, years, flip)
    unique_years = sorted(set(years))

    year_locs = {}
    for year in unique_years:
        yy, xx = np.nonzero(year_grid == year)
        year_locs[year] = (
            xx.max() + 1 + xx.min() if flip else yy.max() + 1 + yy.min()
        ) / 2

    if flip:
        for year, loc in year_locs.items():
            ax.annotate(
                year,
                (loc / year_grid.shape[1], 1),
                (0, 10),
                xycoords="axes fraction",
                textcoords="offset points",
                fontname="monospace",
                fontsize=16,
                va="center",
                ha="center",
            )
    else:
        for year, loc in year_locs.items():
            ax.annotate(
                year,
                (0, 1 - loc / len(year_grid)),
                (-40, 0),
                xycoords="axes fraction",
                textcoords="offset points",
                rotation=90,
                fontname="monospace",
                fontsize=16,
                va="center",
            )
