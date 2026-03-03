from manim import *
import numpy as np

class CSMANonPersistent(Scene):
    def construct(self):
        # ==========================================
        # ЧАСТЬ 1: ИНТЕРФЕЙС
        # ==========================================

        title = Text("Non-persistent CSMA", font_size=40).to_edge(UP, buff=0.2)
        self.add(title)

        scene_shift = DOWN * 0.3
        
        # Устройства
        tx1 = self.create_node("Tx 1", color=BLUE).move_to(LEFT * 5.5 + UP * 2).shift(scene_shift)
        tx2 = self.create_node("Tx 2", color=ORANGE).move_to(LEFT * 5.5 + DOWN * 0.5).shift(scene_shift)
        rx = self.create_node("Rx", color=GREY, is_circle=True).move_to(LEFT * 0.5 + UP * 0.75).shift(scene_shift)
        physical_group = VGroup(tx1, tx2, rx)

        # Алгоритм
        flow_group, flow_steps = self.create_csma_flowchart()
        flow_group.scale(0.95).to_edge(RIGHT, buff=0.3).shift(UP*1.5).shift(scene_shift)
        flow_title = Text("Алгоритм Tx2", font_size=20, color=ORANGE).next_to(flow_group, UP, buff=0.1)

        # Таймлайн
        timeline_axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 3, 1],
            x_length=9,
            y_length=2.0,
            axis_config={"include_tip": True},
            y_axis_config={"include_ticks": False}
        ).to_edge(DOWN, buff=0.5).shift(LEFT*1.5)

        label_row1 = Text("Tx 1", font_size=18, color=BLUE).next_to(timeline_axes.c2p(0, 2), LEFT)
        label_row2 = Text("Tx 2", font_size=18, color=ORANGE).next_to(timeline_axes.c2p(0, 1), LEFT)
        label_time = Text("Время", font_size=18).next_to(timeline_axes.x_axis, RIGHT)
        timeline_group = VGroup(timeline_axes, label_row1, label_row2, label_time)

        self.play(FadeIn(physical_group), Write(flow_group), Write(flow_title), Create(timeline_group))
        
        # --- Вспомогательные функции ---
        
        def highlight(step_key, color=YELLOW):
            if step_key in flow_steps:
                box = flow_steps[step_key]
                self.play(box.animate.set_stroke(color, 4), run_time=0.2)

        def unhighlight(step_key):
            if step_key in flow_steps:
                box = flow_steps[step_key]
                self.play(box.animate.set_stroke(WHITE, 1), run_time=0.2)

        def create_beam(sender, color):
            return Line(start=sender.get_center(), end=sender.get_center(), color=color, stroke_width=8, stroke_opacity=0.6)

        def create_rect(sender, t_start, color):
            y_pos = 2 if sender == tx1 else 1
            start_pos = timeline_axes.c2p(t_start, y_pos)
            rect = Rectangle(width=0.01, height=0.6, fill_color=color, fill_opacity=0.5, stroke_width=0)
            rect.move_to(start_pos, aligned_edge=LEFT)
            return rect

        def get_width_for_duration(duration):
            return duration * (timeline_axes.x_length / 10.0)

        # ==========================================
        # ЧАСТЬ 2: СЦЕНАРИЙ
        # ==========================================

        # 1. Tx1 начинает длинную передачу
        t_start_1 = 1.0
        dur_1 = 3.5 # Длинный пакет
        
        beam1 = create_beam(tx1, BLUE)
        self.add(beam1)
        rect1 = create_rect(tx1, t_start_1, BLUE)
        self.add(rect1)
        
        # Анимация: Tx1 занимает канал
        self.play(
            beam1.animate.put_start_and_end_on(tx1.get_center(), rx.get_center()),
            run_time=0.5
        )
        
        # Tx1 передает часть времени (до момента прихода Tx2)
        t_arrival_2 = 2.0
        w_partial = get_width_for_duration(t_arrival_2 - t_start_1)
        self.play(rect1.animate.stretch_to_fit_width(w_partial, about_edge=LEFT), run_time=1.0, rate_func=linear)

        # 2. Tx2 получает пакет
        highlight("start", ORANGE)
        
        dot_arr = Dot(color=ORANGE).move_to(timeline_axes.c2p(t_arrival_2, 1))
        lbl_arr = Text("Приход пакета", font_size=12, color=ORANGE).next_to(dot_arr, UP, buff=0.1)
        self.play(FadeIn(dot_arr), FadeIn(lbl_arr))
        self.wait(0.5)
        unhighlight("start")

        # 3. Tx2 СЛУШАЕТ КАНАЛ (SENSE)
        highlight("sense", ORANGE)
        
        # Анимация прослушки (волны от Tx2)
        sense_waves = VGroup(*[
            Arc(radius=0.1 + i*0.15, angle=PI, start_angle=0, arc_center=tx2.get_top(), stroke_width=2)
            for i in range(3)
        ]).set_color(ORANGE)
        
        self.play(Create(sense_waves), run_time=0.6)
        self.play(FadeOut(sense_waves))

        # Логика: Канал ЗАНЯТ кем-то другим (Tx1)
        # ИСПРАВЛЕНИЕ: Подсвечиваем Tx1 (источник сигнала)
        busy_lbl = Text("Канал занят Tx1", color=RED, font_size=14).next_to(tx2, UP)
        
        self.play(
            Indicate(tx1, color=RED, scale_factor=1.2), # Tx1 мигает красным
            FadeIn(busy_lbl)
        )
        self.wait(0.5)
        
        # Стрелка "Busy" на схеме
        self.play(Indicate(flow_steps["arrow_busy"], color=RED))
        unhighlight("sense")

        # 4. RANDOM WAIT (Сразу же! Не ждем конца Tx1)
        highlight("wait", ORANGE)
        self.play(FadeOut(busy_lbl))
        
        timer = DecimalNumber(3.0, num_decimal_places=1, color=ORANGE).next_to(flow_steps["wait"], DOWN)
        self.add(timer)
        
        # Пунктирная линия ожидания на графике
        # Tx2 ждет случайное время (например, до t=5.5)
        t_retry = 5.5
        
        dashed = DashedLine(
            start=timeline_axes.c2p(t_arrival_2, 1),
            end=timeline_axes.c2p(t_retry, 1),
            color=GREY
        )
        
        # Пока Tx2 ждет, Tx1 продолжает и заканчивает передачу
        # Tx1 заканчивает в t=4.5
        remaining_duration_tx1 = dur_1 - (t_arrival_2 - t_start_1) # 3.5 - 1.0 = 2.5
        
        # Анимация параллельно: 
        # 1. Таймер Tx2 тикает
        # 2. Пунктир Tx2 растет
        # 3. Tx1 дописывает свой прямоугольник
        
        self.play(
            ChangeDecimalToValue(timer, 0),
            Create(dashed),
            # Tx1 завершает передачу
            rect1.animate.stretch_to_fit_width(get_width_for_duration(dur_1), about_edge=LEFT),
            run_time=2.5, 
            rate_func=linear
        )
        
        # Tx1 убирает луч (канал освободился)
        self.play(
            beam1.animate.put_start_and_end_on(rx.get_center(), rx.get_center()),
            run_time=0.5
        )
        self.remove(beam1)
        
        self.remove(timer, dot_arr, lbl_arr)
        unhighlight("wait")
        
        # Возврат по стрелке
        self.play(ShowPassingFlash(flow_steps["line_return"].copy().set_color(ORANGE)))

        # 5. Tx2 снова СЛУШАЕТ (t=5.5)
        highlight("sense", ORANGE)
        
        sense_waves2 = VGroup(*[
            Arc(radius=0.1 + i*0.15, angle=PI, start_angle=0, arc_center=tx2.get_top(), stroke_width=2)
            for i in range(3)
        ]).set_color(ORANGE)
        self.play(Create(sense_waves2), run_time=0.6)
        self.play(FadeOut(sense_waves2))
        
        # Канал СВОБОДЕН (Никто не светится)
        free_lbl = Text("Свободно", color=GREEN, font_size=16).next_to(tx2, RIGHT)
        self.play(FadeIn(free_lbl))
        self.play(FadeOut(free_lbl))
        
        # Стрелка "Free"
        self.play(Indicate(flow_steps["arrow_free"], color=GREEN))
        unhighlight("sense")

        # 6. Tx2 ПЕРЕДАЕТ
        highlight("send", ORANGE)
        
        beam2 = create_beam(tx2, ORANGE)
        self.add(beam2)
        rect2 = create_rect(tx2, t_retry, ORANGE)
        self.add(rect2)
        
        # Луч летит
        self.play(beam2.animate.put_start_and_end_on(tx2.get_center(), rx.get_center()), run_time=0.3)
        
        # Передача данных
        w_2 = get_width_for_duration(2.0)
        self.play(
            rect2.animate.stretch_to_fit_width(w_2, about_edge=LEFT),
            run_time=1.5, rate_func=linear
        )
        
        # Конец передачи
        self.play(beam2.animate.put_start_and_end_on(rx.get_center(), rx.get_center()), run_time=0.5)
        self.remove(beam2)
        
        self.play(rx.animate.set_fill(GREEN))
        unhighlight("send")

        # ACK
        highlight("ack", ORANGE)
        ack_dot = Dot(color=GREEN).move_to(rx)
        self.play(ack_dot.animate.move_to(tx2), run_time=1.0)
        self.remove(ack_dot)
        self.play(rx.animate.set_fill(GREY))
        
        self.play(Indicate(flow_steps["success"], color=GREEN))
        self.wait(2)


    # --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
    
    def create_node(self, label, color=BLUE, is_circle=False):
        if is_circle:
            shape = Circle(radius=0.35, fill_color=color, fill_opacity=0.2, stroke_color=color)
        else:
            shape = Square(side_length=0.7, fill_color=color, fill_opacity=0.2, stroke_color=color)
        label_obj = Text(label, font_size=16).move_to(shape)
        line = Line(UP*0.35, UP*0.6).move_to(shape.get_top() + UP*0.1)
        arc = Arc(radius=0.15, start_angle=PI/4, angle=PI/2).move_arc_center_to(line.get_end()+DOWN*0.05)
        return VGroup(shape, label_obj, line, arc)

    def create_csma_flowchart(self):
        w = 2.0
        h = 0.5
        
        # --- БЛОКИ ---
        b_start = Rectangle(width=w, height=h, stroke_color=GREY)
        t_start = Text("Начало", font_size=12).move_to(b_start)
        
        b_sense = Polygon(UP*0.3, RIGHT*1.2, DOWN*0.3, LEFT*1.2, color=BLUE).next_to(b_start, DOWN, buff=0.4)
        t_sense = Text("Слушать канал", font_size=12).move_to(b_sense)
        
        # Wait (слева - если занято)
        b_wait = Rectangle(width=1.5, height=h, color=RED).next_to(b_sense, LEFT, buff=0.8)
        t_wait = Text("Ждать\nслучайное\nвремя", font_size=10).move_to(b_wait)
        
        b_send = Rectangle(width=w, height=h, stroke_color=GREY).next_to(b_sense, DOWN, buff=0.6)
        t_send = Text("Отправить пакет", font_size=12).move_to(b_send)
        
        b_ack = Polygon(UP*0.3, RIGHT*1.0, DOWN*0.3, LEFT*1.0, color=WHITE).next_to(b_send, DOWN, buff=0.4)
        t_ack = Text("ACK получен?", font_size=12).move_to(b_ack)
        
        # НОВЫЙ БЛОК: Backoff (справа - если коллизия)
        b_backoff = Rectangle(width=1.5, height=1.5*h, color=RED).next_to(b_ack, RIGHT, buff=0.8)
        t_backoff = Text("Ждать\nслучайное\nвремя", font_size=10).move_to(b_backoff)
        
        b_success = Rectangle(width=w, height=h, color=GREEN).next_to(b_ack, DOWN, buff=0.4)
        t_success = Text("Успех", font_size=12).move_to(b_success)
        
        # --- СТРЕЛКИ ---
        l1 = Arrow(b_start.get_bottom(), b_sense.get_top(), buff=0)
        
        # Занято -> Ждать
        l_busy = Arrow(b_sense.get_left(), b_wait.get_right(), buff=0)
        lbl_busy = Text("Занят", font_size=10, color=RED).next_to(l_busy, UP, buff=0.05)
        
        # Свободно -> Отправить
        l_free = Arrow(b_sense.get_bottom(), b_send.get_top(), buff=0)
        lbl_free = Text("Свободен", font_size=10, color=GREEN).next_to(l_free, RIGHT, buff=0.05)
        
        l2 = Arrow(b_send.get_bottom(), b_ack.get_top(), buff=0)
        
        # ACK -> Yes -> Success
        l_ack_yes = Arrow(b_ack.get_bottom(), b_success.get_top(), buff=0)
        lbl_yes = Text("Да", font_size=10, color=GREEN).next_to(l_ack_yes, RIGHT, buff=0.05)
        
        # ACK -> No -> Backoff (ИСПРАВЛЕНО)
        l_ack_no = Arrow(b_ack.get_right(), b_backoff.get_left(), buff=0)
        lbl_ack_no = Text("Нет", font_size=10, color=RED).next_to(l_ack_no, UP, buff=0.05)
        
        # --- ЛИНИИ ВОЗВРАТА ---
        
        # Точки для маршрутизации наверху
        y_high = (b_start.get_bottom()[1] + b_sense.get_top()[1]) / 2 
        p3_top_sense = [b_sense.get_top()[0], y_high, 0]
        p4_top_sense = b_sense.get_top()

        # 1. Возврат Wait (слева) -> Sense
        p_wait_top = b_wait.get_top()
        p1 = p_wait_top
        p2 = [p1[0], y_high, 0] # Вверх
        
        path_return = VMobject()
        path_return.set_points_as_corners([p1, p2, p3_top_sense, p4_top_sense])
        l_return = VGroup(path_return, Arrow(p3_top_sense, p4_top_sense, buff=0))

        # 2. Возврат Backoff (справа) -> Sense (НОВАЯ ЛИНИЯ)
        p_back_top = b_backoff.get_top()
        pb1 = p_back_top
        pb2 = [pb1[0], y_high, 0] # Вверх на ту же высоту
        
        path_backoff_ret = VMobject()
        path_backoff_ret.set_points_as_corners([pb1, pb2, p3_top_sense, p4_top_sense])
        l_ret_backoff = VGroup(path_backoff_ret, Arrow(p3_top_sense, p4_top_sense, buff=0))

        group = VGroup(
            b_start, t_start, 
            b_sense, t_sense,
            b_wait, t_wait,
            b_send, t_send,
            b_ack, t_ack, b_backoff, t_backoff,
            b_success, t_success,
            l1, l_busy, lbl_busy, l_free, lbl_free, l2, l_ack_yes, lbl_yes,
            l_return, l_ack_no, lbl_ack_no, l_ret_backoff
        )
        
        steps = {
            "start": b_start,
            "sense": b_sense,
            "wait": b_wait,
            "send": b_send,
            "ack": b_ack,
            "backoff": b_backoff,
            "success": b_success,
            "arrow_busy": l_busy,
            "arrow_free": l_free,
            "arrow_ack_yes": l_ack_yes,
            "arrow_ack_no": l_ack_no,
            "line_return": l_return,
            "line_return_back": l_ret_backoff
        }
        
        return group, steps