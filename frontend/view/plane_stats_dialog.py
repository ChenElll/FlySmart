from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QScrollArea,
    QWidget,
    QHBoxLayout,
)
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QPieSeries,
    QBarSeries,
    QBarSet,
    QBarCategoryAxis,
    QValueAxis,
)
from PySide6.QtCore import Qt, QEvent, QPropertyAnimation, QRect
from PySide6.QtGui import QFont, QPainter, QColor
from PySide6.QtWidgets import QLabel



class PlaneStatsDialog(QDialog):
    """חלון דיאגרמות המציג סיכום חזותי של המטוסים המוצגים כרגע."""

    def __init__(self, planes, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window)  # מאפשר מקסום, הצמדה, Alt+Tab
        self.setWindowModality(Qt.NonModal)  # לא חוסם את החלון הראשי
        self.planes = planes

        self.setWindowTitle("Planes Statistics")
        self.resize(900, 650)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #F8FBFD;
            }
            QLabel {
                color: #2F3A4A;
            }
        """
        )

        # ---- מעטפת גלילה ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        scroll.setWidget(inner)

        main_layout = QVBoxLayout(inner)
        self.main_layout = main_layout  # שמירת הפניה ישירה
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(30)

        # כותרת ראשית
        title = QLabel("Planes Overview")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # --- שני תרשימים זה לצד זה (responsive) ---
        self.chart_views = []
        self.charts_row = QHBoxLayout()
        self.charts_row.setSpacing(30)

        self._add_chart(self.charts_row, "Distribution by Manufacturer")
        self._add_chart(self.charts_row, "Planes by Year of Manufacture")

        main_layout.addLayout(self.charts_row)

        # ניטור שינוי גודל חלון (נשתמש בזה כדי להחליף בין אופקי לאנכי)
        self.installEventFilter(self)
        self.is_vertical_layout = False

        # שורת סיכום
        self.summary_label = QLabel("")
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setFont(QFont("Segoe UI", 10))
        self.summary_label.setStyleSheet("color: #4B6E82;")
        main_layout.addWidget(self.summary_label)

        # מעטפת עליונה (כדי לאפשר גלילה)
        container = QWidget()
        outer_layout = QVBoxLayout(container)
        outer_layout.addWidget(scroll)

        main = QVBoxLayout(self)
        main.addWidget(container)

        # טען נתונים
        self.update_charts(planes)

    # ------------------------------------------------------------
    def _add_chart(self, layout, title_text):
        """בונה גרף + כותרת מעליו בתוך מעטפת אנכית."""
        chart_container = QWidget()
        vbox = QVBoxLayout(chart_container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(10)

        # כותרת תמיד מעל
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        vbox.addWidget(title)

        # הגרף עצמו
        chart = QChart()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundVisible(False)
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if "Distribution" in title_text:
            chart_view.setMinimumHeight(350)
        else:
            chart_view.setMinimumHeight(420)
        chart_view.setMinimumWidth(420)

        vbox.addWidget(chart_view)
        layout.addWidget(chart_container)
        self.chart_views.append(chart_view)

    # ------------------------------------------------------------
    def update_charts(self, planes):
        """בניית התרשימים לפי הנתונים"""
        if not planes:
            self.summary_label.setText("No data available.")
            return

        # ======== 1. Pie chart: יצרנים ========
        manufacturer_count = {}
        for p in planes:
            m = getattr(p, "MadeBy", None) or "Unknown"
            manufacturer_count[m] = manufacturer_count.get(m, 0) + 1

        pie_series = QPieSeries()
        for manufacturer, count in manufacturer_count.items():
            pie_series.append(manufacturer, count)
            slice_ = pie_series.slices()[-1]
            slice_.setLabelVisible(True)
            slice_.setLabel(f"{manufacturer} ({count})")

        # --- תגובה בהעברת עכבר + הדגשה של הפרוסה --- #
        def on_hovered(hovered, slice_):
            total = sum(manufacturer_count.values())
            percentage = (slice_.value() / total) * 100

            # אם עובר עכבר על הפרוסה → תבלוט ותעדכן טקסט
            if hovered:
                slice_.setExploded(True)
                slice_.setLabelFont(QFont("Segoe UI", 10, QFont.Bold))
                self.summary_label.setText(
                    f"{slice_.label()}: {slice_.value()} planes ({percentage:.1f}%)"
                )
            else:
                slice_.setExploded(False)
                slice_.setLabelFont(QFont("Segoe UI", 9))
                # שחזור הטקסט הכללי כשהעכבר עוזב
                total = len(planes)
                num_manufacturers = len(manufacturer_count)
                num_years = len({getattr(p, 'Year', 'Unknown') for p in planes})
                self.summary_label.setText(
                    f"Total planes: {total} | Manufacturers: {num_manufacturers} | Years: {num_years}"
                )

        # חיבור לכל הפרוסות
        for s in pie_series.slices():
            s.hovered.connect(lambda hovered, slice_=s: on_hovered(hovered, slice_))



        # מאפשר הצגת פרטים בלחיצה על פרוסה
        def on_slice_clicked(slice_):
            total = sum(manufacturer_count.values())
            percentage = (slice_.value() / total) * 100
            self.summary_label.setText(
                f"{slice_.label()}: {slice_.value()} planes ({percentage:.1f}%)"
            )

        pie_series.slices()[0].clicked.connect(lambda: on_slice_clicked(pie_series.slices()[0]))  # נחבר אחר כך בלולאה
        for s in pie_series.slices():
            s.clicked.connect(lambda checked=False, slice_=s: on_slice_clicked(slice_))


        chart1 = self.chart_views[0].chart()
        chart1.removeAllSeries()
        chart1.addSeries(pie_series)
        chart1.setTitle("Distribution by Manufacturer")

        # ======== 2. Bar chart: לפי שנת ייצור ========
        year_count = {}
        for p in planes:
            y = str(getattr(p, "Year", None) or "Unknown")
            year_count[y] = year_count.get(y, 0) + 1

        bar_set = QBarSet("Planes")
        bar_set.setColor(QColor("#4BA3C7"))
        bar_set.setBorderColor(QColor("#357A9D"))

        # רק 10 השנים האחרונות
        years_sorted = sorted(
            [y for y in year_count.keys() if y.isdigit()], key=lambda x: int(x)
        )
        recent_years = years_sorted[-10:] if len(years_sorted) > 10 else years_sorted

        for y in recent_years:
            bar_set << year_count[y]

        bar_series = QBarSeries()
        bar_series.append(bar_set)
        bar_series.setBarWidth(0.4)

        chart2 = self.chart_views[1].chart()
        chart2.removeAllSeries()
        chart2.addSeries(bar_series)
        chart2.setTitle("Planes by Year of Manufacture")

        # ניקוי צירים ישנים
        for axis in chart2.axes():
            chart2.removeAxis(axis)

        # ציר X
        axis_x = QBarCategoryAxis()
        axis_x.append(recent_years)
        if len(recent_years) > 5:
            axis_x.setLabelsAngle(-45)
        chart2.addAxis(axis_x, Qt.AlignBottom)
        bar_series.attachAxis(axis_x)

        # ציר Y
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        axis_y.setTitleText("Number of Planes")
        chart2.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_y)

        chart2.legend().setAlignment(Qt.AlignBottom)
        chart2.setAnimationOptions(QChart.SeriesAnimations)

        # תווית קטנה שמוצגת מעל העמודה
        hover_label = QLabel(self.chart_views[1])
        hover_label.setStyleSheet("""
            background-color: #ffffff;
            color: #2F3A4A;
            border: 1px solid #C0D6E4;
            border-radius: 5px;
            padding: 3px 6px;
            font-size: 10pt;
        """)
        hover_label.hide()

            # --- תגובה בהעברת עכבר לגרף העמודות --- #
        hover_label = QLabel(self.chart_views[1])
        hover_label.setStyleSheet("""
            background-color: #ffffff;
            color: #2F3A4A;
            border: 1px solid #C0D6E4;
            border-radius: 5px;
            padding: 3px 6px;
            font-size: 10pt;
        """)
        hover_label.hide()

        def on_bar_hovered(status, index):
            if 0 <= index < len(recent_years):
                year = recent_years[index]
                count = bar_set.at(index)

                # המרת ערכים לקואורדינטות מסך
                plot_area = chart2.plotArea()
                x_axis = chart2.axes(Qt.Horizontal)[0]
                y_axis = chart2.axes(Qt.Vertical)[0]

                # חישוב מיקום יחסי לפי הציר X
                x_min = x_axis.min()
                x_max = x_axis.max() if hasattr(x_axis, "max") else len(recent_years) - 1
                step = plot_area.width() / max(1, len(recent_years))
                x = plot_area.left() + (index + 0.5) * step

                # חישוב גובה העמודה לפי ערך Y
                y_val = count
                y_min, y_max = y_axis.min(), y_axis.max()
                ratio = (y_val - y_min) / max(1, y_max - y_min)
                y = plot_area.bottom() - (ratio * plot_area.height())

                if status:
                    bar_set.setColor(QColor("#2F7FA1"))
                    hover_label.setText(f"{year}: {count} planes")
                    hover_label.adjustSize()
                    hover_label.move(int(x - hover_label.width() / 2), int(y - 40))
                    hover_label.show()
                    hover_label.raise_()
                else:
                    bar_set.setColor(QColor("#4BA3C7"))
                    hover_label.hide()

        bar_set.hovered.connect(on_bar_hovered)


        # ======== סיכום ========
        total = len(planes)
        num_manufacturers = len(manufacturer_count)
        num_years = len(year_count)
        self.summary_label.setText(
            f"Total planes: {total} | Manufacturers: {num_manufacturers} | Years: {num_years}"
        )

    # ------------------------------------------------------------
    def eventFilter(self, obj, event):
        """משנה את סידור התרשימים (אופקי / אנכי) לפי גודל החלון"""
        if event.type() == QEvent.Resize:
            width = self.width()
            # מתחת לרוחב מסוים - פריסה אנכית
            if width < 950 and not self.is_vertical_layout:
                self._switch_to_vertical()
            elif width >= 950 and self.is_vertical_layout:
                self._switch_to_horizontal()
        return super().eventFilter(obj, event)

    def _switch_to_vertical(self):
        """מעביר את התרשימים אחד מתחת לשני"""
        self.is_vertical_layout = True
        self._rebuild_charts_layout(Qt.Vertical)

    def _switch_to_horizontal(self):
        """מעביר את התרשימים זה לצד זה"""
        self.is_vertical_layout = False
        self._rebuild_charts_layout(Qt.Horizontal)

    def _rebuild_charts_layout(self, orientation):
        """בונה מחדש את פריסת התרשימים בצורה חלקה"""
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout

        # מאתרים את ה-layout הראשי שמכיל את התרשימים
        parent_layout = self.main_layout
        all_widgets = []

        # שומרים את הווידג'טים הקיימים (הגרפים עם הכותרות)
        for i in range(self.charts_row.count()):
            item = self.charts_row.itemAt(i)
            if item and item.widget():
                all_widgets.append(item.widget())

        # יוצרים layout חדש בהתאם לכיוון הרצוי
        if orientation == Qt.Vertical:
            new_layout = QVBoxLayout()
        else:
            new_layout = QHBoxLayout()
            new_layout.setSpacing(30)

        # מוסיפים את כל התרשימים (עם הכותרות) מחדש
        for widget in all_widgets:
            self.charts_row.removeWidget(widget)
            widget.setParent(None)
            new_layout.addWidget(widget)

                # מחפשים את המיקום המדויק של charts_row בתוך parent_layout
        index_to_replace = -1
        for i in range(parent_layout.count()):
            item = parent_layout.itemAt(i)
            if item and item.layout() == self.charts_row:
                index_to_replace = i
                break

        # מחליפים לפי אינדקס אמיתי, או מוסיפים בסוף אם לא נמצא
        if index_to_replace != -1:
            parent_layout.takeAt(index_to_replace)
            parent_layout.insertLayout(index_to_replace, new_layout)
        else:
            parent_layout.addLayout(new_layout)

        self.charts_row = new_layout
