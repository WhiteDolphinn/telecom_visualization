from manim import *

class AlohaPhysic(Scene):
    def construct(self):
        # --- 1. НАСТРОЙКА ИНТЕРФЕЙСА ---
        
        # Левая часть: Физический мир
        tx1 = self.create_node("Tx 1", color=BLUE).move_to(LEFT * 5.5 + UP * 2)
        tx2 = self.create_node("Tx 2", color=ORANGE).move_to(LEFT * 5.5 + DOWN * 0.5)
        rx = self.create_node("Rx", color=GREY, is_circle=True).move_to(LEFT * 0.5 + UP * 0.75)
        
        physical_group = VGroup(tx1, tx2, rx)
        
        # Правая часть: Блок-схема
        flow_group, flow_steps = self.create_flowchart()
        flow_group.scale(0.7).to_edge(RIGHT, buff=0.3).shift(UP*0.5)
        
        # Нижняя часть: Временная шкала
        timeline_axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 3, 1],
            x_length=9,
            y_length=2.0,
            axis_config={"include_tip": True, "tip_width": 0.15, "tip_height": 0.15},
            y_axis_config={"include_ticks": False}
        ).to_edge(DOWN, buff=0.5).shift(LEFT*1.5)
        
        label_row1 = Text("Tx 1", font_size=18, color=BLUE).next_to(timeline_axes.c2p(0, 2), LEFT)
        label_row2 = Text("Tx 2", font_size=18, color=ORANGE).next_to(timeline_axes.c2p(0, 1), LEFT)
        label_time = Text("Time (t)", font_size=18).next_to(timeline_axes.x_axis, RIGHT)
        
        timeline_group = VGroup(timeline_axes, label_row1, label_row2, label_time)
        
        self.play(FadeIn(physical_group), Write(flow_group), Create(timeline_group))
        
        # --- ПАРАМЕТРЫ СИМУЛЯЦИИ ---
        # 1 единица timeline_x соответствует 1 секунде
        prop_time = 0.5  # Время полета сигнала от Tx до Rx
        
        # --- ФУНКЦИИ ---
        
        def highlight(step_key, color=YELLOW):
            box = flow_steps[step_key][0]
            self.play(box.animate.set_stroke(color, 4), run_time=0.2)

        def unhighlight(step_key):
            box = flow_steps[step_key][0]
            self.play(box.animate.set_stroke(WHITE, 1), run_time=0.2)

        def create_beam(sender, color):
            # Луч начинается и заканчивается в точке отправителя (длина 0)
            return Line(start=sender.get_center(), end=sender.get_center(), color=color, stroke_width=8, stroke_opacity=0.6)

        def create_rect(sender, t_arrival, color):
            y_pos = 2 if sender == tx1 else 1
            start_pos = timeline_axes.c2p(t_arrival, y_pos)
            rect = Rectangle(width=0.01, height=0.6, fill_color=color, fill_opacity=0.5, stroke_width=0)
            rect.move_to(start_pos, aligned_edge=LEFT)
            return rect

        def get_width_for_duration(duration):
            return duration * (timeline_axes.x_length / 10.0)

        # Функция "Нормальной" передачи (без коллизий)
        def run_success_sequence(sender, t_start, duration, color):
            # 1. Луч летит (Propagation)
            beam = create_beam(sender, color)
            self.add(beam)
            
            # Луч долетает до Rx за prop_time
            self.play(
                beam.animate.put_start_and_end_on(sender.get_center(), rx.get_center()),
                run_time=prop_time, rate_func=linear
            )
            
            # 2. Только теперь создаем прямоугольник! (Сигнал дошел)
            t_arrival = t_start + prop_time
            rect = create_rect(sender, t_arrival, color)
            self.add(rect)
            
            # 3. Передача тела пакета
            # Луч стоит на месте (связь есть), прямоугольник растет
            # Длительность фазы "держания" канала
            hold_time = duration - prop_time 
            # (мы упрощаем: пакет "вытекает" целиком, потом "хвост" летит. 
            # Для визуала сделаем: prop_time (рост) + duration (течение) + prop_time (спад) - это долго.
            # Сделаем проще: общее время занятия Rx = duration.
            
            width_full = get_width_for_duration(duration)
            
            # Растем до конца
            self.play(
                rect.animate.stretch_to_fit_width(width_full, about_edge=LEFT),
                run_time=duration, rate_func=linear
            )
            
            # 4. Завершение (Хвост улетает в Rx)
            self.play(
                beam.animate.put_start_and_end_on(rx.get_center(), rx.get_center()),
                run_time=prop_time, rate_func=linear
            )
            self.remove(beam)
            return rect

        # --- СЦЕНАРИЙ ---
        
        # 1. Start
        highlight("start")
        self.wait(0.5)
        unhighlight("start")
        highlight("send")
        
        # --- СЛОЖНАЯ СЦЕНА КОЛЛИЗИИ ---
        # Tx1 Start: t=1.0. Arrival: t=1.5. Duration: 2.0. Ends at Rx: 3.5.
        # Tx2 Start: t=2.0. Arrival: t=2.5. Duration: 2.0. Ends at Rx: 4.5.
        
        beam1 = create_beam(tx1, BLUE)
        beam2 = create_beam(tx2, ORANGE)
        self.add(beam1)
        
        # ЭТАП 1: Tx1 летит к Rx (t=1.0 -> 1.5)
        self.play(
            beam1.animate.put_start_and_end_on(tx1.get_center(), rx.get_center()),
            run_time=0.5, rate_func=linear
        )
        
        # ЭТАП 2: Tx1 принят, рисуем Rect1. Tx2 молчит (t=1.5 -> 2.0)
        # Rect1 начинает расти ТОЛЬКО СЕЙЧАС
        rect1 = create_rect(tx1, 1.5, BLUE)
        self.add(rect1)
        
        width_05 = get_width_for_duration(0.5)
        self.play(
            rect1.animate.stretch_to_fit_width(width_05, about_edge=LEFT),
            run_time=0.5, rate_func=linear
        )
        
        # ЭТАП 3: Tx2 начинает передачу, летит к Rx. Tx1 продолжает лить данные (t=2.0 -> 2.5)
        self.add(beam2)
        # Rect1 продолжает расти (уже 1.0 длины)
        width_10 = get_width_for_duration(1.0)
        
        self.play(
            # Tx2 летит
            beam2.animate.put_start_and_end_on(tx2.get_center(), rx.get_center()),
            # Tx1 продолжает
            rect1.animate.stretch_to_fit_width(width_10, about_edge=LEFT),
            run_time=0.5, rate_func=linear
        )
        
        # ЭТАП 4: МОМЕНТ УДАРА (t=2.5). Rect2 появляется.
        rect2 = create_rect(tx2, 2.5, ORANGE)
        self.add(rect2)
        
        # Включаем коллизию!
        bang = Text("Collision!", color=RED, font_size=24).next_to(rx, UP)
        self.add(bang)
        beam1.set_color(RED)
        beam2.set_color(RED)
        
        # ЭТАП 5: ОБА передают до конца Tx1 (t=2.5 -> 3.5)
        # Это длится 1.0 сек.
        # Tx1 заканчивается в 3.5. Tx2 будет на середине.
        
        # Tx1 должен "втянуться" в Rx в конце этого этапа?
        # Давайте упростим: визуально луч стоит, пока идет передача.
        # В конце пакета луч "улетает".
        
        # Tx1 (total dur 2.0) заканчивается. Rect1 grows to full width.
        # Tx2 (total dur 2.0) grows to 1.0 width.
        
        width_full = get_width_for_duration(2.0)
        
        # Одновременная передача "ломаных" пакетов
        self.play(
            # Rect1 дорастает до конца
            rect1.animate.stretch_to_fit_width(width_full, about_edge=LEFT),
            # Rect2 растет
            rect2.animate.stretch_to_fit_width(width_10, about_edge=LEFT),
            # Визуальный шум на лучах
            Wiggle(beam1, rotation_angle=0.01*TAU, run_time=1.0),
            Wiggle(beam2, rotation_angle=0.01*TAU, run_time=1.0),
            Flash(rx, color=RED, run_time=1.0, flash_radius=0.5),
            run_time=1.0, rate_func=linear
        )
        
        # Tx1 закончился. Хвост улетает. (t=3.5 -> 4.0)
        # Tx2 продолжает (еще 0.5 сек)
        width_15 = get_width_for_duration(1.5)
        
        self.play(
            beam1.animate.put_start_and_end_on(rx.get_center(), rx.get_center()), # Tx1 исчезает
            rect2.animate.stretch_to_fit_width(width_15, about_edge=LEFT),
            Wiggle(beam2, rotation_angle=0.01*TAU, run_time=0.5), # Tx2 все еще страдает
            run_time=0.5, rate_func=linear
        )
        self.remove(beam1)
        
        # ЭТАП 6: Tx2 завершает передачу (t=4.0 -> 4.5)
        # Tx2 заканчивается.
        self.play(
            rect2.animate.stretch_to_fit_width(width_full, about_edge=LEFT),
            Wiggle(beam2, rotation_angle=0.01*TAU, run_time=0.5),
            run_time=0.5, rate_func=linear
        )
        
        # Хвост Tx2 улетает
        self.play(
            beam2.animate.put_start_and_end_on(rx.get_center(), rx.get_center()),
            run_time=0.5, rate_func=linear
        )
        self.remove(beam2)
        
        # Отмечаем зону коллизии на графике (задним числом, для ясности)
        # Пересечение с t=2.5 (Start Rx2) до t=3.5 (End Rx1)
        col_start_x = timeline_axes.c2p(2.5, 0)[0]
        col_end_x = timeline_axes.c2p(3.5, 0)[0]
        col_width = col_end_x - col_start_x
        
        col_zone = Rectangle(width=col_width, height=2.2, fill_color=RED, fill_opacity=0.3, stroke_width=0)
        col_zone.move_to(timeline_axes.c2p(2.5, 1.5), aligned_edge=LEFT)
        self.play(FadeIn(col_zone))
        
        unhighlight("send")
        
        # 2. ACK Check
        highlight("ack")
        self.wait(0.5)
        self.play(Indicate(flow_steps["arrow_no"], color=RED))
        unhighlight("ack")
        
        # 3. Wait
        highlight("wait")
        self.play(FadeOut(bang))
        
        # Пунктир ожидания
        timer = DecimalNumber(2.0, num_decimal_places=1, color=RED).next_to(flow_steps["wait"][0], LEFT)
        self.add(timer)
        
        # Ждем с t=5.0 (примерно) до t=7.0
        wait_start = 5.0
        wait_end = 7.0
        
        dashed = DashedLine(
            start=timeline_axes.c2p(wait_start, 2),
            end=timeline_axes.c2p(wait_end, 2),
            color=GREY
        )
        
        self.play(
            ChangeDecimalToValue(timer, 0),
            Create(dashed),
            run_time=1.5
        )
        self.remove(timer)
        unhighlight("wait")
        self.play(ShowPassingFlash(flow_steps["line_return"].copy().set_color(YELLOW)))
        
        # 4. Success Retry
        highlight("send")
        
        # Tx1 пробует снова в t=7.0
        run_success_sequence(tx1, 7.0, 2.0, BLUE)
        
        self.play(rx.animate.set_fill(GREEN))
        unhighlight("send")
        
        highlight("ack")
        ack_dot = Dot(color=GREEN, radius=0.1).move_to(rx.get_center())
        self.play(ack_dot.animate.move_to(tx1.get_center()), run_time=0.5)
        self.remove(ack_dot)
        self.play(rx.animate.set_fill(GREY))
        
        self.play(Indicate(flow_steps["arrow_yes"], color=GREEN))
        unhighlight("ack")
        
        highlight("success", color=GREEN)
        self.play(Indicate(flow_steps["success"]))
        
        self.wait(2)

    # --- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ---
    def create_node(self, label, color=BLUE, is_circle=False):
        if is_circle:
            shape = Circle(radius=0.4, fill_color=color, fill_opacity=0.2, stroke_color=color)
        else:
            shape = Square(side_length=0.8, fill_color=color, fill_opacity=0.2, stroke_color=color)
        
        label_obj = Text(label, font_size=20).move_to(shape)
        return VGroup(shape, label_obj)

    def create_flowchart(self):
        w = 2.5
        b_start = Rectangle(width=w, height=0.6)
        t_start = Text("Packet Ready", font_size=16).move_to(b_start)
        g_start = VGroup(b_start, t_start)
        
        b_send = Rectangle(width=w, height=0.6).next_to(b_start, DOWN, buff=0.6)
        t_send = Text("Send Packet", font_size=16).move_to(b_send)
        g_send = VGroup(b_send, t_send)
        
        b_ack = Polygon(UP*0.5, RIGHT*1.2, DOWN*0.5, LEFT*1.2, color=WHITE).next_to(b_send, DOWN, buff=0.6)
        t_ack = Text("Got ACK?", font_size=16).move_to(b_ack)
        g_ack = VGroup(b_ack, t_ack)
        
        b_wait = Rectangle(width=1.8, height=0.6, color=RED).next_to(b_ack, LEFT, buff=0.8)
        t_wait = Text("Random Wait", font_size=14).move_to(b_wait)
        g_wait = VGroup(b_wait, t_wait)
        
        b_success = Rectangle(width=w, height=0.6, color=GREEN).next_to(b_ack, DOWN, buff=0.6)
        t_success = Text("Success", font_size=16).move_to(b_success)
        g_success = VGroup(b_success, t_success)
        
        l1 = Arrow(b_start.get_bottom(), b_send.get_top(), buff=0)
        l2 = Arrow(b_send.get_bottom(), b_ack.get_top(), buff=0)
        l_yes = Arrow(b_ack.get_bottom(), b_success.get_top(), buff=0)
        lbl_yes = Text("Yes", font_size=12, color=GREEN).next_to(l_yes, RIGHT, buff=0.05)
        l_no = Arrow(b_ack.get_left(), b_wait.get_right(), buff=0)
        lbl_no = Text("No", font_size=12, color=RED).next_to(l_no, UP, buff=0.05)
        
        path = VMobject()
        p1, p2, p3 = b_wait.get_top(), b_wait.get_top() + UP * 1.2, b_send.get_left()
        path.set_points_as_corners([p1, p2, [p3[0], p2[1], 0], p3])
        l_return = VGroup(path, Arrow(path.get_points()[-2], p3, buff=0))
        
        group = VGroup(g_start, g_send, g_ack, g_wait, g_success, l1, l2, l_yes, lbl_yes, l_no, lbl_no, l_return)
        steps = {"start": g_start, "send": g_send, "ack": g_ack, "wait": g_wait, "success": g_success, "arrow_yes": l_yes, "arrow_no": l_no, "line_return": l_return}
        return group, steps