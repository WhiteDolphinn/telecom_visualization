from manim import *
import numpy as np

class SlottedAlohaComplete(Scene):
    def construct(self):
        # ==========================================
        # ЧАСТЬ 1: ФИЗИЧЕСКАЯ СИМУЛЯЦИЯ
        # ==========================================

        title = Text("Slotted Aloha", font_size=40).to_edge(UP, buff=0.2)
        self.add(title)

        scene_shift = DOWN * 0.3
        
        # --- Настройка интерфейса ---
        tx1 = self.create_node("Tx 1", color=BLUE).move_to(LEFT * 5.5 + UP * 2).shift(scene_shift)
        tx2 = self.create_node("Tx 2", color=ORANGE).move_to(LEFT * 5.5 + DOWN * 0.5).shift(scene_shift)
        rx = self.create_node("Rx", color=GREY, is_circle=True).move_to(LEFT * 0.5 + UP * 0.75).shift(scene_shift)
        physical_group = VGroup(tx1, tx2, rx)

        flow_group, flow_steps = self.create_flowchart()
        flow_group.scale(1.1).to_edge(RIGHT, buff=0.3).shift(UP).shift(scene_shift)
        flow_title = Text("Алгоритм Tx1", font_size=20, color=BLUE).next_to(flow_group, UP, buff=0.2)

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
        label_time = Text("Время (t)", font_size=18).next_to(timeline_axes.x_axis, RIGHT)
        
        # Сетка слотов (каждые 2 секунды)
        slot_duration = 2.0
        grid_lines = VGroup()
        for t in range(0, 11, int(slot_duration)):
            line = DashedLine(
                start=timeline_axes.c2p(t, 0),
                end=timeline_axes.c2p(t, 2.8),
                color=GRAY, stroke_opacity=0.5
            )
            grid_lines.add(line)
            # if t < 10:
                # slot_num = Text(f"Slot {t//2}", font_size=12, color=GRAY).move_to(timeline_axes.c2p(t + 1, 2.8))
                # grid_lines.add(slot_num)

        timeline_group = VGroup(timeline_axes, grid_lines, label_row1, label_row2, label_time)

        self.play(FadeIn(physical_group), Write(flow_group), Write(flow_title), Create(timeline_group))
        
        # --- Вспомогательные функции ---
        def highlight(step_key, color=YELLOW):
            box = flow_steps[step_key]
            self.play(box.animate.set_stroke(color, 4), run_time=0.2)

        def unhighlight(step_key):
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

        # --- СЦЕНАРИЙ ---

        # 1. Приход пакетов (Асинхронно в Slot 0)
        highlight("start")
        
        t_slot_start = 2.0
        
        # Точки прихода
        dot1 = Dot(color=BLUE).move_to(timeline_axes.c2p(0.5, 2))
        lbl_arr1 = Text("Приход пакета", font_size=12, color=BLUE).next_to(dot1, UP, buff=0.1)
        
        dot2 = Dot(color=ORANGE).move_to(timeline_axes.c2p(1.2, 1))
        lbl_arr2 = Text("Приход пакета", font_size=12, color=ORANGE).next_to(dot2, DOWN, buff=0.1)
        
        wait1 = DashedLine(timeline_axes.c2p(0.5, 2), timeline_axes.c2p(2.0, 2), color=BLUE_A)
        wait2 = DashedLine(timeline_axes.c2p(1.2, 1), timeline_axes.c2p(2.0, 1), color=ORANGE)
        
        self.play(FadeIn(dot1), FadeIn(lbl_arr1))
        self.play(FadeIn(dot2), FadeIn(lbl_arr2))
        self.play(Create(wait1), Create(wait2), run_time=0.5)
        
        unhighlight("start")
        
        # 2. Синхронный старт в Slot 1 (t=2.0)
        highlight("send")
        
        beam1 = create_beam(tx1, BLUE)
        beam2 = create_beam(tx2, ORANGE)
        self.add(beam1, beam2)

        self.play(
            beam1.animate.put_start_and_end_on(tx1.get_center(), rx.get_center()),
            beam2.animate.put_start_and_end_on(tx2.get_center(), rx.get_center()),
            run_time=0.5, rate_func=linear
        )
        
        # Прямоугольники
        rect1 = create_rect(tx1, t_slot_start, BLUE)
        rect2 = create_rect(tx2, t_slot_start, ORANGE)
        self.remove(dot1, dot2, wait1, wait2, lbl_arr1, lbl_arr2)
        self.add(rect1, rect2)
        
        width_full = get_width_for_duration(slot_duration)
        
        # Коллизия
        bang = Text("Коллизия!", color=RED, font_size=24).next_to(rx, UP)
        self.add(bang)
        beam1.set_color(RED); beam2.set_color(RED)
        
        self.play(
            rect1.animate.stretch_to_fit_width(width_full, about_edge=LEFT),
            rect2.animate.stretch_to_fit_width(width_full, about_edge=LEFT),
            Wiggle(beam1, rotation_angle=0.01*TAU, run_time=1.5),
            Wiggle(beam2, rotation_angle=0.01*TAU, run_time=1.5),
            Flash(rx, color=RED, run_time=1.5),
            run_time=1.5, rate_func=linear
        )
        
        self.play(
            beam1.animate.put_start_and_end_on(rx.get_center(), rx.get_center()),
            beam2.animate.put_start_and_end_on(rx.get_center(), rx.get_center()),
            run_time=0.5, rate_func=linear
        )
        self.remove(beam1, beam2)

        # Зона коллизии
        col_zone = Rectangle(width=width_full, height=2.2, fill_color=RED, fill_opacity=0.3, stroke_width=0)
        col_zone.move_to(timeline_axes.c2p(3.0, 1.5)) 
        self.play(FadeIn(col_zone))
        
        unhighlight("send")
        
        # ACK error
        highlight("ack"); self.wait(0.2)
        self.play(Indicate(flow_steps["arrow_no"], color=RED)); unhighlight("ack")
        
        highlight("wait"); self.play(FadeOut(bang))
        
        # Бэкофф
        timer1 = DecimalNumber(1, num_decimal_places=0, color=RED).next_to(flow_steps["wait"], LEFT)
        t_lbl1 = Text("slot", font_size=12, color=RED).next_to(timer1, DOWN, buff=0.1)
        self.add(timer1, t_lbl1)
        
        # t_lbl2 = Text("Wait 2 slots", font_size=14, color=ORANGE).next_to(timeline_axes.c2p(5.0, 1), DOWN)
        # self.play(Write(t_lbl2))

        dashed_wait1 = DashedLine(start=timeline_axes.c2p(4.3, 2), end=timeline_axes.c2p(6.0, 2), color=GREY)
        dashed_wait2 = DashedLine(start=timeline_axes.c2p(4.3, 1), end=timeline_axes.c2p(8.0, 1), color=ORANGE)
        
        self.play(
            ChangeDecimalToValue(timer1, 0), 
            Create(dashed_wait1),
            Create(dashed_wait2),
            run_time=1.5
        )
        self.remove(timer1, t_lbl1); unhighlight("wait")
        self.play(ShowPassingFlash(flow_steps["line_return"].copy().set_color(YELLOW)))
        
        # 4. Успех Tx1 (Slot 3)
        highlight("send")
        t_retry = 6.0
        t2_retry = 8.0
        
        beam_suc = create_beam(tx1, BLUE)
        self.add(beam_suc)
        rect_suc = create_rect(tx1, t_retry, BLUE)
        # rect_suc2 = create_rect(tx2, t2_retry, ORANGE)
        
        self.play(beam_suc.animate.put_start_and_end_on(tx1.get_center(), rx.get_center()), run_time=0.5)
        self.add(rect_suc)
        
        
        self.play(rect_suc.animate.stretch_to_fit_width(width_full, about_edge=LEFT), run_time=1.5)
        self.play(beam_suc.animate.put_start_and_end_on(rx.get_center(), rx.get_center()), run_time=0.5)
        self.remove(beam_suc)
        
        self.play(rx.animate.set_fill(GREEN))
        unhighlight("send")

        
        highlight("ack")
        ack_packet = Dot(color=GREEN, radius=0.15).move_to(rx.get_center())
        ack_label = Text("ACK", font_size=12, color=GREEN).next_to(ack_packet, UP, buff=0.1)
        ack_group = VGroup(ack_packet, ack_label)
        
        self.add(ack_group)
        self.play(ack_group.animate.move_to(tx1.get_center()), run_time=1.0, rate_func=linear)
        self.remove(ack_group)
        self.play(rx.animate.set_fill(GREY))
        
        self.play(Indicate(flow_steps["success"], color=GREEN))
        
        # self.play(FadeOut(t_lbl2), FadeOut(dashed_wait2))
        self.wait(1)

        beam_suc2 = create_beam(tx2, ORANGE)
        self.add(beam_suc2)
        rect_suc2 = create_rect(tx2, t2_retry, ORANGE)

        self.play(beam_suc2.animate.put_start_and_end_on(tx2.get_center(), rx.get_center()), run_time=0.5)
        self.add(rect_suc2)

        self.play(rect_suc2.animate.stretch_to_fit_width(width_full, about_edge=LEFT), run_time=1.5)
        self.play(beam_suc2.animate.put_start_and_end_on(rx.get_center(), rx.get_center()), run_time=0.5)
        self.remove(beam_suc2)

        # ==========================================
        # ЧАСТЬ 2: ПЕРЕХОД К МАТЕМАТИКЕ
        # ==========================================
        
        self.play(
            FadeOut(rect1), FadeOut(rect2), FadeOut(rect_suc), FadeOut(rect_suc2), 
            FadeOut(col_zone), FadeOut(dashed_wait1), FadeOut(title), FadeOut(dashed_wait2),
            rx.animate.set_fill(GREY)
        )

        shift_amount = UP * 2.8
        everything = VGroup(physical_group, flow_group, flow_title, timeline_group)
        self.play(everything.animate.shift(shift_amount), run_time=1.5)

           # ==========================================
        # ЧАСТЬ 3: АНАЛИЗ
        # ==========================================

        math_title = Text("Вывод пропускной способности", font_size=24, color=YELLOW)
        math_title.next_to(timeline_axes, DOWN, buff=0.2)
        self.play(Write(math_title))

        # Эталонный пакет Tx1 в Слоте 2 (t=4..6)
        # Обратите внимание: координаты после сдвига, но c2p генерирует абсолютные.
        # Так как мы сдвинули оси через animate.shift, сам объект axes изменил положение.
        t_ref_start = 4.0
        w_ref = get_width_for_duration(slot_duration)
        
        ref_rect = Rectangle(width=w_ref, height=0.6, fill_color=BLUE, fill_opacity=0.6, stroke_width=0)
        ref_rect.move_to(timeline_axes.c2p(t_ref_start, 2), aligned_edge=LEFT)
        self.play(FadeIn(ref_rect))
        
        # Призрачный пакет (показываем логику прихода)
        # Он может прийти в ЛЮБОЕ время в предыдущем слоте (t=2..4)
        t_danger_start = 2.0
        t_danger_end = 4.0
        
        # Зона опасности - это Слот 1
        p_left = timeline_axes.c2p(t_danger_start, 1)
        p_right = timeline_axes.c2p(t_danger_end, 1)
        
        # Рисуем "Точку прихода"
        dot_ghost = Dot(color=ORANGE).move_to(timeline_axes.c2p(t_danger_start, 1))
        lbl_ghost = Text("Приход пакета", font_size=14, color=ORANGE).next_to(dot_ghost, UP, buff=0.1)
        
        # Пунктир, показывающий, что он ждет начала след. слота
        wait_ghost = DashedLine(
            start=dot_ghost.get_center(),
            end=timeline_axes.c2p(4.0, 1),
            color=ORANGE
        )
        
        self.play(FadeIn(dot_ghost), FadeIn(lbl_ghost))
        
        # Движение точки прихода по всему опасному интервалу
        self.play(Create(wait_ghost))
        
        # Анимация: двигаем точку прихода с t=2.0 до t=4.0
        # Линия ожидания должна сокращаться
        def wait_updater(m):
            current_start = dot_ghost.get_center()
            target_end = timeline_axes.c2p(4.0, 1)
            # Если точка переехала границу, линия исчезает
            if current_start[0] >= target_end[0]:
                m.put_start_and_end_on(target_end, target_end)
            else:
                m.put_start_and_end_on(current_start, target_end)

        wait_ghost.add_updater(wait_updater)
        lbl_ghost.add_updater(lambda m: m.next_to(dot_ghost, UP, buff=0.1))
        
        # Пакет Tx2, который появится в t=4.0
        rect_collision = Rectangle(width=w_ref, height=0.6, fill_color=ORANGE, fill_opacity=0.4, stroke_width=0)
        rect_collision.move_to(timeline_axes.c2p(4.0, 1), aligned_edge=LEFT)
        
        # Движение
        self.play(
            dot_ghost.animate.move_to(timeline_axes.c2p(4.0, 1)),
            run_time=3.0, rate_func=linear
        )
        
        # Как только дошли до 4.0, показываем, что пакет ТУТ ЖЕ начинается -> Коллизия
        self.play(FadeIn(rect_collision), ref_rect.animate.set_color(RED))
        col_txt = Text("Коллизия!", color=RED, font_size=16).next_to(rect_collision, DOWN, buff=0.1)
        self.play(Write(col_txt))
        self.wait(1)
        
        # Очистка
        wait_ghost.clear_updaters()
        lbl_ghost.clear_updaters()
        self.play(
            FadeOut(dot_ghost), FadeOut(lbl_ghost), FadeOut(wait_ghost), 
            FadeOut(rect_collision), FadeOut(col_txt),
            ref_rect.animate.set_color(BLUE)
        )

        # --- ФОРМУЛЫ ---
        
        # Скобка интервала уязвимости (1 слот)
        brace_vul = Brace(Line(p_left, p_right), DOWN, buff=0.1)
        
        txt_vul = VGroup(
            Text("Коллизионный интервал =", font_size=16),
            MathTex(r"\Delta t", font_size=20)
        ).arrange(RIGHT, buff=0.1).next_to(brace_vul, DOWN).shift(UP * 0.25)

        self.play(GrowFromCenter(brace_vul), Write(txt_vul))

        # Формулы
        f1 = VGroup(
            Text("Вероятность успеха:", font_size=20),
            MathTex(r"P_{success} = P(0) = e^{- \lambda \Delta t}", font_size=26)
        ).arrange(RIGHT, buff=0.2)
        
        f2 = VGroup(
            Text("Пропускная способность:", font_size=20),
            MathTex(r"S = \lambda \cdot P_{success} = \lambda \cdot e^{- \lambda}", font_size=26),
            Text("принимая", font_size=20),
            MathTex(r"\Delta t = 1", font_size=26)
        ).arrange(RIGHT, buff=0.2)
        
        formulas = VGroup(f1, f2).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        formulas.next_to(math_title, DOWN, buff=0.2)
        # formulas.scale(0.9)
        # formulas.to_edge(DOWN, buff=0.5)
        
        self.play(Write(formulas))
        self.play(Create(SurroundingRectangle(f2, color=YELLOW, buff=0.1)))
        
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
        b_send = Rectangle(width=w, height=0.75, stroke_color=GREY).next_to(b_start, DOWN, buff=0.4)
        b_ack = Polygon(UP*0.4, RIGHT*1.0, DOWN*0.4, LEFT*1.0, color=WHITE).next_to(b_send, DOWN, buff=0.4)
        b_wait = Rectangle(width=1.5, height=0.75, color=RED).next_to(b_ack, LEFT, buff=0.6)
        b_success = Rectangle(width=w, height=0.5, color=GREEN).next_to(b_ack, DOWN, buff=0.4)
        
        l1 = Arrow(b_start.get_bottom(), b_send.get_top(), buff=0)
        l2 = Arrow(b_send.get_bottom(), b_ack.get_top(), buff=0)
        l_no = Arrow(b_ack.get_left(), b_wait.get_right(), buff=0)
        l_yes = Arrow(b_ack.get_bottom(), b_success.get_top(), buff=0)
        
        path = VMobject()
        p1, p2, p3 = b_wait.get_top(), b_wait.get_top() + UP * 1.0, b_send.get_left()
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
        t2 = Text("Отправить\nв начале\nслота", font_size=12).move_to(b_send)
        t3 = Text("ACK?", font_size=12).move_to(b_ack)
        t4 = Text("Ждать\nслучайное\nвремя", font_size=12).move_to(b_wait)
        t5 = Text("Конец", font_size=12).move_to(b_success)
        group.add(t1, t2, t3, t4, t5)
        
        return group, steps