from manim import *
import numpy as np

class AlohaComplete(Scene):
    def construct(self):
        # ==========================================
        # ЧАСТЬ 1: ФИЗИЧЕСКАЯ СИМУЛЯЦИЯ
        # ==========================================

        # --- 0. ЗАГОЛОВОК ---
        title = Text("Pure Aloha", font_size=48).to_edge(UP, buff=0.5)
        self.add(title)

        # --- 1.1 Настройка интерфейса ---
        # Сдвинем чуть вниз, чтобы не наезжать на заголовок
        scene_shift = DOWN * 0.3
        
        # Левая часть: Устройства
        tx1 = self.create_node("Tx 1", color=BLUE).move_to(LEFT * 5.5 + UP * 2).shift(scene_shift)
        tx2 = self.create_node("Tx 2", color=ORANGE).move_to(LEFT * 5.5 + DOWN * 0.5).shift(scene_shift)
        rx = self.create_node("Rx", color=GREY, is_circle=True).move_to(LEFT * 0.5 + UP * 0.75).shift(scene_shift)
        physical_group = VGroup(tx1, tx2, rx)

        # Правая часть: Алгоритм
        flow_group, flow_steps = self.create_flowchart()
        flow_group.scale(1.0).to_edge(RIGHT, buff=0.3).shift(UP*0.5).shift(scene_shift)
        flow_title = Text("Алгоритм Tx1", font_size=20, color=BLUE).next_to(flow_group, UP, buff=0.1)

        # Нижняя часть: Таймлайн
        timeline_axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 3, 1],
            x_length=9,
            y_length=2.0,
            axis_config={"include_tip": True},
            y_axis_config={"include_ticks": False}
        ).to_edge(DOWN, buff=0.5).shift(LEFT*1.5)

        label_row1 = Text("Tx1", font_size=18, color=BLUE).next_to(timeline_axes.c2p(0, 2), LEFT)
        label_row2 = Text("Tx2", font_size=18, color=ORANGE).next_to(timeline_axes.c2p(0, 1), LEFT)
        label_time = Text("Time (t)", font_size=18).next_to(timeline_axes.x_axis, RIGHT)
        timeline_group = VGroup(timeline_axes, label_row1, label_row2, label_time)

        # Показываем всё
        self.play(FadeIn(physical_group), Write(flow_group), Write(flow_title), Create(timeline_group))
        
        # --- Функции ---
        
        def highlight(step_key, color=YELLOW):
            box = flow_steps[step_key]
            self.play(box.animate.set_stroke(color, 4), run_time=0.2)

        def unhighlight(step_key):
            box = flow_steps[step_key]
            self.play(box.animate.set_stroke(WHITE, 1), run_time=0.2)

        def create_beam(sender, color):
            return Line(start=sender.get_center(), end=sender.get_center(), color=color, stroke_width=8, stroke_opacity=0.6)

        def create_rect(sender, t_arrival, color):
            y_pos = 2 if sender == tx1 else 1
            start_pos = timeline_axes.c2p(t_arrival, y_pos)
            rect = Rectangle(width=0.01, height=0.6, fill_color=color, fill_opacity=0.5, stroke_width=0)
            rect.move_to(start_pos, aligned_edge=LEFT)
            return rect

        def get_width_for_duration(duration):
            return duration * (timeline_axes.x_length / 10.0)

        # --- СЦЕНАРИЙ ---
        
        # 1. Старт
        highlight("start")
        self.wait(0.2)
        unhighlight("start")
        highlight("send")

        # 2. Коллизия
        beam1 = create_beam(tx1, BLUE)
        beam2 = create_beam(tx2, ORANGE)
        self.add(beam1)

        # Tx1 летит
        self.play(beam1.animate.put_start_and_end_on(tx1.get_center(), rx.get_center()), run_time=0.5, rate_func=linear)
        
        # Tx1 график
        rect1 = create_rect(tx1, 1.5, BLUE)
        self.add(rect1)
        width_05 = get_width_for_duration(0.5)
        self.play(rect1.animate.stretch_to_fit_width(width_05, about_edge=LEFT), run_time=0.5, rate_func=linear)

        # Tx2 начинает
        self.add(beam2)
        width_10 = get_width_for_duration(1.0)
        self.play(
            beam2.animate.put_start_and_end_on(tx2.get_center(), rx.get_center()),
            rect1.animate.stretch_to_fit_width(width_10, about_edge=LEFT),
            run_time=0.5, rate_func=linear
        )

        # Удар
        rect2 = create_rect(tx2, 2.5, ORANGE)
        self.add(rect2)
        
        bang = Text("Коллизия!", color=RED, font_size=24).next_to(rx, UP)
        self.add(bang)
        beam1.set_color(RED); beam2.set_color(RED)

        # Передача продолжается (оба испорчены)
        width_full = get_width_for_duration(2.0)
        self.play(
            rect1.animate.stretch_to_fit_width(width_full, about_edge=LEFT),
            rect2.animate.stretch_to_fit_width(width_10, about_edge=LEFT),
            Wiggle(beam1, rotation_angle=0.01*TAU, run_time=1.0),
            Wiggle(beam2, rotation_angle=0.01*TAU, run_time=1.0),
            Flash(rx, color=RED, run_time=1.0),
            run_time=1.0, rate_func=linear
        )

        # Tx1 завершение
        width_15 = get_width_for_duration(1.5)
        self.play(
            beam1.animate.put_start_and_end_on(rx.get_center(), rx.get_center()),
            rect2.animate.stretch_to_fit_width(width_15, about_edge=LEFT),
            Wiggle(beam2, rotation_angle=0.01*TAU, run_time=0.5),
            run_time=0.5, rate_func=linear
        )
        self.remove(beam1)

        # Tx2 завершение
        self.play(
            rect2.animate.stretch_to_fit_width(width_full, about_edge=LEFT),
            Wiggle(beam2, rotation_angle=0.01*TAU, run_time=0.5),
            run_time=0.5, rate_func=linear
        )
        self.play(beam2.animate.put_start_and_end_on(rx.get_center(), rx.get_center()), run_time=0.5, rate_func=linear)
        self.remove(beam2)

        # Зона коллизии
        col_zone = Rectangle(width=get_width_for_duration(1.0), height=2.2, fill_color=RED, fill_opacity=0.3, stroke_width=0)
        col_zone.move_to(timeline_axes.c2p(3.0, 1.5)) 
        self.play(FadeIn(col_zone))

        unhighlight("send")

        # Ошибка ACK
        highlight("ack"); self.wait(0.2)
        self.play(Indicate(flow_steps["arrow_no"], color=RED)); unhighlight("ack")
        
        # Ожидание
        highlight("wait"); self.play(FadeOut(bang))
        
        timer = DecimalNumber(2.0, num_decimal_places=1, color=RED).next_to(flow_steps["wait"], LEFT)
        self.add(timer)
        dashed = DashedLine(start=timeline_axes.c2p(4.0, 2), end=timeline_axes.c2p(6.0, 2), color=GREY)
        self.play(ChangeDecimalToValue(timer, 0), Create(dashed), run_time=1.0)
        self.remove(timer); unhighlight("wait")
        self.play(ShowPassingFlash(flow_steps["line_return"].copy().set_color(YELLOW)))

        # 3. Успешная отправка
        highlight("send")
        
        beam_suc = create_beam(tx1, BLUE)
        self.add(beam_suc)
        rect_suc = create_rect(tx1, 6, BLUE)
        
        self.play(beam_suc.animate.put_start_and_end_on(tx1.get_center(), rx.get_center()), run_time=0.3)
        self.add(rect_suc)
        self.play(rect_suc.animate.stretch_to_fit_width(width_full, about_edge=LEFT), run_time=1.0)
        self.play(beam_suc.animate.put_start_and_end_on(rx.get_center(), rx.get_center()), run_time=0.3)
        self.remove(beam_suc)
        
        self.play(rx.animate.set_fill(GREEN))
        unhighlight("send")
        
        # --- ИСПРАВЛЕНИЕ: Видимый полет ACK ---
        highlight("ack")
        
        # Создаем пакет ACK
        ack_packet = Dot(color=GREEN, radius=0.15).move_to(rx.get_center())
        ack_label = Text("ACK", font_size=12, color=GREEN).next_to(ack_packet, UP, buff=0.1)
        # Группируем точку и текст, чтобы летели вместе
        ack_group = VGroup(ack_packet, ack_label)
        
        self.add(ack_group)
        # Летит от RX к TX1
        self.play(ack_group.animate.move_to(tx1.get_center()), run_time=1.0, rate_func=linear)
        self.remove(ack_group)
        self.play(rx.animate.set_fill(GREY))
        
        self.play(Indicate(flow_steps["success"], color=GREEN))
        self.wait(1)

        # ==========================================
        # ЧАСТЬ 2: ПЕРЕХОД К МАТЕМАТИКЕ
        # ==========================================
        
        self.play(
            FadeOut(rect1), FadeOut(rect2), FadeOut(rect_suc), 
            FadeOut(col_zone), FadeOut(dashed), FadeOut(title), # Убираем заголовок Pure Aloha
            rx.animate.set_fill(GREY)
        )

        shift_amount = UP * 2.3
        everything = VGroup(physical_group, flow_group, flow_title, timeline_group)
        
        self.play(everything.animate.shift(shift_amount), run_time=1.5)

        # ==========================================
        # ЧАСТЬ 3: АНАЛИЗ
        # ==========================================

        math_title = Text("Вывод пропускной способности", font_size=24, color=YELLOW)
        math_title.next_to(timeline_axes, DOWN, buff=0.2)
        self.play(Write(math_title))

        t_ref_start = 4.0
        duration = 2.0
        w_ref = get_width_for_duration(duration)
        
        ref_rect = Rectangle(width=w_ref, height=0.6, fill_color=BLUE, fill_opacity=0.6, stroke_width=0)
        ref_rect.move_to(timeline_axes.c2p(t_ref_start, 2), aligned_edge=LEFT)
        self.play(FadeIn(ref_rect))
        
        ghost_rect = Rectangle(width=w_ref, height=0.6, fill_color=ORANGE, fill_opacity=0.4, stroke_color=ORANGE, stroke_width=2)
        ghost_rect.move_to(timeline_axes.c2p(0.5, 1), aligned_edge=LEFT)
        
        lbl_ghost = Text("Чужой пакет", font_size=14, color=ORANGE).next_to(ghost_rect, UP, buff=0.1)
        lbl_ghost.add_updater(lambda m: m.next_to(ghost_rect, UP, buff=0.1))
        
        self.play(FadeIn(ghost_rect), FadeIn(lbl_ghost))

        danger_start = t_ref_start - duration
        danger_end = t_ref_start + duration
        
        danger_start_pt = timeline_axes.c2p(danger_start, 1)
        danger_line = Line(start=danger_start_pt, end=danger_start_pt + RIGHT*0.01, color=RED, stroke_width=8)
        self.add(danger_line)

        self.play(ghost_rect.animate.move_to(timeline_axes.c2p(danger_start, 1), aligned_edge=LEFT), run_time=1.5)
        
        col_txt = Text("Коллизия!", color=RED, font_size=16).next_to(ghost_rect, DOWN).shift(UP * 0.2)
        self.play(FadeIn(col_txt))

        def danger_updater(m):
            curr_x = ghost_rect.get_left()[0]
            start_pt = timeline_axes.c2p(danger_start, 1)
            if curr_x <= start_pt[0]: curr_x = start_pt[0] + 0.01
            end_arr = np.array([curr_x, start_pt[1], 0])
            if np.linalg.norm(end_arr - start_pt) < 0.001:
                end_arr = start_pt + np.array([0.001, 0, 0])
            m.put_start_and_end_on(start_pt, end_arr)

        danger_line.add_updater(danger_updater)

        self.play(
            ghost_rect.animate.move_to(timeline_axes.c2p(danger_end, 1), aligned_edge=LEFT),
            ref_rect.animate.set_color(RED),
            run_time=3.0, rate_func=linear
        )
        danger_line.remove_updater(danger_updater)
        
        self.play(FadeOut(col_txt), ref_rect.animate.set_color(BLUE))
        self.play(FadeOut(ghost_rect), FadeOut(lbl_ghost))

        # --- ФОРМУЛЫ ---
        p_left = timeline_axes.c2p(danger_start, 1)
        p_right = timeline_axes.c2p(danger_end, 1)
        brace_vul = Brace(Line(p_left, p_right), DOWN, buff=0.1)
        
        txt_vul = VGroup(
            Text("Коллизионный интервал =", font_size=16),
            MathTex(r"2 \Delta t", font_size=20)
        ).arrange(RIGHT, buff=0.1).next_to(brace_vul, DOWN).shift(UP * 0.25)

        self.play(GrowFromCenter(brace_vul), Write(txt_vul))

        f1 = VGroup(
            Text("Вероятность успеха:", font_size=20),
            MathTex(r"P_{success} = P(0) = e^{-2 \lambda \Delta t}", font_size=26)
        ).arrange(RIGHT, buff=0.2).shift(DOWN * 0.8)
        
        f2 = VGroup(
            Text("Пропускная способность:", font_size=20),
            MathTex(r"S = \lambda P_{success} = \lambda \cdot e^{-2 \lambda }", font_size=26),
            Text("принимая", font_size=20),
            MathTex(r"\Delta t = 1", font_size=26)
        ).arrange(RIGHT, buff=0.2).shift(DOWN * 0.4)
        
        formulas = VGroup(f1, f2).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        formulas.next_to(math_title, DOWN, buff=0.2)
        
        if formulas.get_bottom()[1] < -3.5:
            formulas.shift(UP * 0.5)
        
        self.play(Write(formulas))
        self.play(Create(SurroundingRectangle(f2, color=YELLOW)))
        
        self.wait(3)

    # --- ВСПОМОГАТЕЛЬНЫЕ ---
    def create_node(self, label, color=BLUE, is_circle=False):
        if is_circle:
            shape = Circle(radius=0.35, fill_color=color, fill_opacity=0.2, stroke_color=color)
        else:
            shape = Square(side_length=0.7, fill_color=color, fill_opacity=0.2, stroke_color=color)
        label_obj = Text(label, font_size=16).move_to(shape)
        line = Line(UP*0.35, UP*0.6).move_to(shape.get_top() + UP*0.1)
        arc = Arc(radius=0.15, start_angle=PI/4, angle=PI/2).move_arc_center_to(line.get_end()+DOWN*0.05)
        return VGroup(shape, label_obj, line, arc)

    def create_flowchart(self):
        w = 2.0
        b_start = Rectangle(width=w, height=0.5, stroke_color=GREY)
        b_send = Rectangle(width=w, height=0.5, stroke_color=GREY).next_to(b_start, DOWN, buff=0.4)
        b_ack = Polygon(UP*0.4, RIGHT*1.0, DOWN*0.4, LEFT*1.0, color=WHITE).next_to(b_send, DOWN, buff=0.4)
        b_wait = Rectangle(width=1.5, height=0.75, color=RED).next_to(b_ack, LEFT, buff=0.6)
        b_success = Rectangle(width=w, height=0.5, color=GREEN).next_to(b_ack, DOWN, buff=0.4)
        
        l1 = Arrow(b_start.get_bottom(), b_send.get_top(), buff=0)
        l2 = Arrow(b_send.get_bottom(), b_ack.get_top(), buff=0)
        l_no = Arrow(b_ack.get_left(), b_wait.get_right(), buff=0)
        l_yes = Arrow(b_ack.get_bottom(), b_success.get_top(), buff=0)
        
        path = VMobject()
        p1, p2, p3 = b_wait.get_top(), b_wait.get_top() + UP * 0.7, b_send.get_left()
        path.set_points_as_corners([p1, p2, [p3[0], p2[1], 0], p3])
        l_return = VGroup(path, Arrow(path.get_points()[-2], p3, buff=0))

        group = VGroup(b_start, b_send, b_ack, b_wait, b_success, l1, l2, l_no, l_yes, l_return)
        
        steps = {
            "start": b_start, 
            "send": b_send, 
            "ack": b_ack, 
            "wait": b_wait, 
            "success": b_success, 
            "arrow_no": l_no, 
            "line_return": l_return
        }
        
        t1 = Text("Начало", font_size=12).move_to(b_start)
        t2 = Text("Отправить", font_size=12).move_to(b_send)
        t3 = Text("ACK?", font_size=12).move_to(b_ack)
        t4 = Text("Ждать\nслучайное\nвремя", font_size=12).move_to(b_wait)
        t5 = Text("Конец", font_size=12).move_to(b_success)
        group.add(t1, t2, t3, t4, t5)
        
        return group, steps