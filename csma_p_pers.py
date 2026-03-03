from manim import *
import numpy as np

class CSMAPPersistent(Scene):
    def construct(self):
        # ==========================================
        # ЧАСТЬ 1: ИНТЕРФЕЙС (НОВАЯ КОМПОНОВКА)
        # ==========================================

        # Заголовок чуть выше
        title = Text("P-persistent CSMA", font_size=32).to_edge(UP, buff=0.1)
        self.add(title)

        # --- 1. ТОПОЛОГИЯ СЕТИ (ВЕРХНЯЯ ЧАСТЬ) ---
        # Располагаем Tx в ряд сверху, Rx под ними
        
        # Координаты для Tx
        y_tx = 2
        tx1 = self.create_node("Tx 1", color=BLUE).move_to(LEFT * 5.5 + UP * y_tx)
        tx2 = self.create_node("Tx 2", color=ORANGE).move_to(LEFT * 2.5 + UP * y_tx)
        tx3 = self.create_node("Tx 3", color=TEAL).move_to(RIGHT * 0.5 + UP * y_tx)
        
        # Rx по центру под ними
        rx = self.create_node("Rx", color=GREY, is_circle=True).move_to(LEFT * 2.5 + UP * 0.5)
        
        physical_group = VGroup(tx1, tx2, tx3, rx)

        # --- 2. АЛГОРИТМ (ПРАВАЯ ЧАСТЬ) ---
        flow_group, flow_steps = self.create_p_persistent_flowchart()
        flow_group.scale(1.05).to_edge(RIGHT, buff=0.2).shift(UP*1.25)
        flow_title = Text("Алгоритм", font_size=16, color=WHITE).next_to(flow_group, UP, buff=0.1)

        # --- 3. ТАЙМЛАЙН (НИЖНЯЯ ЧАСТЬ) ---
        # Сдвигаем вниз и влево, чтобы не мешать алгоритму
        timeline_axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 4, 1], # 0..3 (3 строки)
            x_length=8,
            y_length=3,      # Чуть компактнее по высоте
            axis_config={"include_tip": True},
            y_axis_config={"include_ticks": False}
        ).to_edge(DOWN, buff=0.5).shift(LEFT*2)

        # Подписи строк (Tx1 выше, Tx3 ниже)
        label_row1 = Text("Tx 1", font_size=16, color=BLUE).next_to(timeline_axes.c2p(0, 2.5), LEFT)
        label_row2 = Text("Tx 2", font_size=16, color=ORANGE).next_to(timeline_axes.c2p(0, 1.5), LEFT)
        label_row3 = Text("Tx 3", font_size=16, color=TEAL).next_to(timeline_axes.c2p(0, 0.5), LEFT)
        label_time = Text("Время", font_size=16).next_to(timeline_axes.x_axis, RIGHT)
        
        # Сетка слотов
        grid_lines = VGroup()
        for t in range(0, 11):
            line = DashedLine(
                start=timeline_axes.c2p(t, 0),
                end=timeline_axes.c2p(t, 3.0),
                color=GRAY, stroke_opacity=0.7
            )
            grid_lines.add(line)
            
        timeline_group = VGroup(timeline_axes, grid_lines, label_row1, label_row2, label_row3, label_time)

        self.play(FadeIn(physical_group), Write(flow_group), Write(flow_title), Create(timeline_group))
        
        # --- Функции ---
        def highlight(step_key, color=YELLOW):
            if step_key in flow_steps:
                self.play(flow_steps[step_key].animate.set_stroke(color, 4), run_time=0.2)

        def unhighlight(step_key):
            if step_key in flow_steps:
                self.play(flow_steps[step_key].animate.set_stroke(WHITE, 1), run_time=0.2)

        def create_beam(sender, color):
            # Луч от отправителя к Rx
            return Line(start=sender.get_center(), end=sender.get_center(), color=color, stroke_width=6, stroke_opacity=0.6)

        def create_rect(sender, t_start, color):
            # Определяем Y уровень на графике
            # Tx1 -> y=2.5 (верхняя полоса)
            # Tx2 -> y=1.5 (средняя)
            # Tx3 -> y=0.5 (нижняя)
            if sender == tx1: y = 2.5
            elif sender == tx2: y = 1.5
            else: y = 0.5
            
            start_pos = timeline_axes.c2p(t_start, y)
            # Высота прямоугольника чуть меньше 1, чтобы не слипались
            rect = Rectangle(width=0.01, height=0.6, fill_color=color, fill_opacity=0.6, stroke_width=0)
            rect.move_to(start_pos, aligned_edge=LEFT)
            return rect

        def get_width(duration):
            return duration * (timeline_axes.x_length / 10.0)

        # ==========================================
        # ЧАСТЬ 2: СЦЕНАРИЙ
        # ==========================================

        # 1. Tx1 начинает передачу (t=1.0)
        t_start_1 = 1.0
        dur_1 = 3.0 # до t=4.0
        
        beam1 = create_beam(tx1, BLUE)
        rect1 = create_rect(tx1, t_start_1, BLUE)
        self.add(beam1, rect1)
        
        self.play(beam1.animate.put_start_and_end_on(tx1.get_center(), rx.get_center()), run_time=0.5)
        
        # Tx1 передает... (частично)
        self.play(rect1.animate.stretch_to_fit_width(get_width(1.5), about_edge=LEFT), run_time=1.0, rate_func=linear)

        # 2. Tx2 и Tx3 приходят (t=2.5)
        t_arr = 2.5
        # Точки на графике
        dot2 = Dot(color=ORANGE).move_to(timeline_axes.c2p(t_arr, 1.5))
        dot3 = Dot(color=TEAL).move_to(timeline_axes.c2p(t_arr, 0.5))
        
        # Подпись теперь не перекроет Tx, так как Tx высоко
        lbl_arr = Text("Приход пакета", font_size=12).next_to(dot2, UP, buff=0.1)
        
        self.play(FadeIn(dot2), FadeIn(dot3), FadeIn(lbl_arr))
        self.wait(0.5)
        
        # 3. Они слушают канал -> ЗАНЯТО
        highlight("sense", YELLOW)
        
        # Волны от 2 и 3
        waves = VGroup(
            *[Arc(radius=0.1+i*0.1, angle=PI, start_angle=PI, arc_center=n.get_bottom(), color=c) 
              for n, c in [(tx2, ORANGE), (tx3, TEAL)] for i in range(2)]
        )
        self.play(Create(waves), run_time=0.5); self.play(FadeOut(waves))
        
        # Tx1 красный (занят)
        self.play(Indicate(tx1, color=RED), Indicate(flow_steps["arrow_busy"], color=RED))
        
        # Пунктиры ожидания до конца слота (t=3.0)
        wait2 = DashedLine(timeline_axes.c2p(t_arr, 1.5), timeline_axes.c2p(3.0, 1.5), color=ORANGE)
        wait3 = DashedLine(timeline_axes.c2p(t_arr, 0.5), timeline_axes.c2p(3.0, 0.5), color=TEAL)
        
        self.play(
            Create(wait2), Create(wait3),
            rect1.animate.stretch_to_fit_width(get_width(2.0), about_edge=LEFT), # Tx1 до t=3.0
            run_time=0.5, rate_func=linear
        )
        unhighlight("sense")
        self.play(FadeOut(dot2), FadeOut(dot3), FadeOut(lbl_arr))

        # 4. Проверка в t=3.0 -> Всё еще занято
        # Tx1 всё еще передает (до 4.0)
        wait2_b = DashedLine(timeline_axes.c2p(3.0, 1.5), timeline_axes.c2p(4.0, 1.5), color=ORANGE)
        wait3_b = DashedLine(timeline_axes.c2p(3.0, 0.5), timeline_axes.c2p(4.0, 0.5), color=TEAL)
        
        self.play(
            Create(wait2_b), Create(wait3_b),
            rect1.animate.stretch_to_fit_width(get_width(dur_1), about_edge=LEFT), # Tx1 до t=4.0
            run_time=1.0, rate_func=linear
        )
        
        # Tx1 закончил
        self.play(beam1.animate.put_start_and_end_on(rx.get_center(), rx.get_center()), run_time=0.3)
        self.remove(beam1)
        
        # 5. МОМЕНТ ИСТИНЫ (t=4.0) - Канал свободен
        highlight("sense", YELLOW)
        self.play(Indicate(flow_steps["arrow_free"], color=GREEN))
        unhighlight("sense")
        
        # 6. Бросок вероятности (Prob Check)
        highlight("prob", YELLOW)
        
        # Показываем решение над устройствами
        # Текст над Tx2 и Tx3 (теперь места много)
        res2 = Text("p -> Отправить", color=GREEN, font_size=14).next_to(tx2, UP)
        res3 = Text("1-p -> Ждать", color=YELLOW, font_size=14).next_to(tx3, UP)
        
        self.play(Write(res2), Write(res3))
        self.wait(1)
        
        self.play(
            Indicate(flow_steps["arrow_send"], color=GREEN),
            Indicate(flow_steps["arrow_wait"], color=YELLOW)
        )
        unhighlight("prob")
        
        # 7. Исполнение решений
        
        # Tx2 Начинает передачу
        highlight("send", ORANGE)
        beam2 = create_beam(tx2, ORANGE)
        rect2 = create_rect(tx2, 4.0, ORANGE)
        self.add(beam2, rect2)
        
        # Tx3 Ждет (рисуем пунктир на следующий слот t=4 -> t=5)
        highlight("wait_slot", TEAL)
        wait3_c = DashedLine(timeline_axes.c2p(4.0, 0.5), timeline_axes.c2p(5.0, 0.5), color=TEAL)
        
        # Текст "Нет коллизии!" справа от Rx
        no_col = Text("Свободно!", font_size=16, color=GREEN).next_to(rx, RIGHT)
        
        self.play(
            # Tx2 летит
            beam2.animate.put_start_and_end_on(tx2.get_center(), rx.get_center()),
            # Tx3 ждет
            Create(wait3_c),
            FadeIn(no_col),
            run_time=0.5
        )
        
        # Передача данных Tx2 (до t=5.0)
        self.play(
            rect2.animate.stretch_to_fit_width(get_width(1.0), about_edge=LEFT),
            run_time=1.0, rate_func=linear
        )
        unhighlight("wait_slot")
        
        # В t=5.0 Tx3 снова проверяет канал.
        # Видит, что Tx2 занят
        highlight("sense", TEAL)
        self.play(Indicate(tx2, color=RED)) 
        unhighlight("sense")
        
        # Tx3 ждет до t=6.0
        wait3_d = DashedLine(timeline_axes.c2p(5.0, 0.5), timeline_axes.c2p(6.0, 0.5), color=TEAL)
        
        self.play(
            rect2.animate.stretch_to_fit_width(get_width(2.0), about_edge=LEFT), # Tx2 finish at 6.0
            Create(wait3_d),
            run_time=1.0, rate_func=linear
        )
        
        # Tx2 Заканчивает
        self.play(beam2.animate.put_start_and_end_on(rx.get_center(), rx.get_center()), run_time=0.3)
        self.remove(beam2)
        unhighlight("send")
        
        # Tx2 получает ACK (маленькая точка)
        ack_dot = Dot(color=GREEN).move_to(rx)
        self.play(ack_dot.animate.move_to(tx2), run_time=0.5)
        self.remove(ack_dot)
        self.play(Indicate(flow_steps["success"], color=GREEN))
        
        # Очистка
        self.play(FadeOut(res2), FadeOut(res3), FadeOut(no_col))
        
        # 8. Теперь Tx3 (t=6.0)
        highlight("sense", TEAL)
        self.play(Indicate(flow_steps["arrow_free"], color=GREEN))
        unhighlight("sense")
        
        # Бросает монетку -> Теперь Успех (p)
        highlight("prob", TEAL)
        res3_b = Text("p -> Отправить", color=GREEN, font_size=14).next_to(tx3, UP)
        self.play(Write(res3_b))
        unhighlight("prob")
        
        # Tx3 Передает
        highlight("send", TEAL)
        beam3 = create_beam(tx3, TEAL)
        rect3 = create_rect(tx3, 6.0, TEAL)
        self.add(beam3, rect3)
        
        self.play(beam3.animate.put_start_and_end_on(tx3.get_center(), rx.get_center()), run_time=0.3)
        self.play(rect3.animate.stretch_to_fit_width(get_width(2.0), about_edge=LEFT), run_time=1.5)
        self.play(beam3.animate.put_start_and_end_on(rx.get_center(), rx.get_center()), run_time=0.3)
        self.remove(beam3)
        
        # Success Tx3
        highlight("success", GREEN)
        self.play(Indicate(flow_steps["success"], color=GREEN))
        
        self.wait(2)

    # --- ВСПОМОГАТЕЛЬНЫЕ ---
    def create_node(self, label, color=BLUE, is_circle=False):
        if is_circle:
            shape = Circle(radius=0.35, fill_color=color, fill_opacity=0.2, stroke_color=color)
        else:
            shape = Square(side_length=0.6, fill_color=color, fill_opacity=0.2, stroke_color=color)
        label_obj = Text(label, font_size=14).move_to(shape)
        line = Line(UP*0.3, UP*0.5).move_to(shape.get_top() + UP*0.1)
        arc = Arc(radius=0.1, start_angle=PI/4, angle=PI/2).move_arc_center_to(line.get_end()+DOWN*0.05)
        return VGroup(shape, label_obj, line, arc)

    def create_p_persistent_flowchart(self):
        w = 1.8
        h = 0.5
        
        # --- БЛОКИ ---
        b_start = Rectangle(width=w, height=h, stroke_color=GREY)
        t_start = Text("Начало", font_size=10).move_to(b_start)
        
        b_sense = Polygon(UP*0.3, RIGHT*1.0, DOWN*0.3, LEFT*1.0, color=BLUE).next_to(b_start, DOWN, buff=0.3)
        t_sense = Text("Слушать", font_size=10).move_to(b_sense)
        
        # Wait Slot (Слева от Sense)
        b_wait_slot = Rectangle(width=1.2, height=h, color=YELLOW).next_to(b_sense, LEFT, buff=0.5)
        t_wait_slot = Text("Ждать\nслот", font_size=10).move_to(b_wait_slot)
        
        # Probability (Внизу от Sense)
        b_prob = Polygon(UP*0.5, RIGHT*1.2, DOWN*0.5, LEFT*1.2, color=ORANGE).next_to(b_sense, DOWN, buff=0.4)
        t_prob = Text("Отправка\nс вероятностью p", font_size=10).move_to(b_prob)
        
        # Send (Внизу от Prob)
        # b_send = Rectangle(width=w, height=h, stroke_color=GREY).next_to(b_prob, DOWN, buff=0.4)
        # t_send = Text("Отправить", font_size=10).move_to(b_send)
        
        # --- НОВЫЕ БЛОКИ ---
        # ACK (Внизу от Send)
        b_ack = Polygon(UP*0.3, RIGHT*1.0, DOWN*0.3, LEFT*1.0, color=WHITE).next_to(b_prob, DOWN, buff=0.4)
        t_ack = Text("ACK?", font_size=10).move_to(b_ack)
        
        # Backoff (Слева от ACK - при коллизии)
        b_backoff = Rectangle(width=1.2, height=1.5*h, color=RED).next_to(b_ack, RIGHT, buff=0.8)
        t_backoff = Text("Ждать\nслучайное\nвремя", font_size=10).move_to(b_backoff)
        
        # Success (Внизу от ACK)
        b_success = Rectangle(width=w, height=h, color=GREEN).next_to(b_ack, DOWN, buff=0.4)
        t_success = Text("Успех", font_size=10).move_to(b_success)
        
        # --- СТРЕЛКИ ---
        l1 = Arrow(b_start.get_bottom(), b_sense.get_top(), buff=0)
        
        # Sense -> Busy -> Wait Slot
        l_busy = Arrow(b_sense.get_left(), b_wait_slot.get_right(), buff=0)
        lbl_busy = Text("Занят", font_size=8, color=RED).next_to(l_busy, UP, buff=0.02)
        
        # Sense -> Free -> Prob
        l_free = Arrow(b_sense.get_bottom(), b_prob.get_top(), buff=0)
        lbl_free = Text("Свободен", font_size=8, color=GREEN).next_to(l_free, RIGHT, buff=0.02)
        
        # Prob -> p -> Send
        l_send = Arrow(b_prob.get_bottom(), b_ack.get_top(), buff=0)
        lbl_p = Text("Да", font_size=8, color=GREEN).next_to(l_send, RIGHT, buff=0.02)
        
        # Prob -> 1-p -> Wait Slot
        path_wait = VMobject()
        pp1 = b_prob.get_left()
        pp2 = [b_wait_slot.get_bottom()[0], pp1[1], 0]
        pp3 = b_wait_slot.get_bottom()
        path_wait.set_points_as_corners([pp1, pp2, pp3])
        l_wait_prob = VGroup(path_wait, Arrow(pp2, pp3, buff=0))
        # Исправлено позиционирование текста 1-p
        lbl_1p = Text("Нет", font_size=8, color=YELLOW).next_to(pp1, LEFT, buff=0.05).shift(UP*0.1)
        
        # Send -> ACK
        # l_to_ack = Arrow(b_send.get_bottom(), b_ack.get_top(), buff=0)
        
        # ACK -> Yes -> Success
        l_ack_yes = Arrow(b_ack.get_bottom(), b_success.get_top(), buff=0)
        lbl_yes = Text("Да", font_size=8, color=GREEN).next_to(l_ack_yes, RIGHT, buff=0.02)
        
        # ACK -> No -> Backoff
        l_ack_no = Arrow(b_ack.get_right(), b_backoff.get_left(), buff=0)
        lbl_no = Text("Нет", font_size=8, color=RED).next_to(l_ack_no, UP, buff=0.02)
        
        # --- ЛИНИИ ВОЗВРАТА ---
        
        # Общая высота для возврата (между Start и Sense)
        y_high = (b_start.get_bottom()[1] + b_sense.get_top()[1]) / 2 
        
        # Точка входа в Sense сверху
        p_sense_in = b_sense.get_top()
        # Точка поворота над Sense
        p_turn_sense = [p_sense_in[0], y_high, 0]

        # 1. Wait Slot -> Sense
        pw1 = b_wait_slot.get_top()
        pw2 = [pw1[0], y_high, 0]
        
        path_ret = VMobject()
        path_ret.set_points_as_corners([pw1, pw2, p_turn_sense, p_sense_in])
        l_ret_slot = VGroup(path_ret, Arrow(p_turn_sense, p_sense_in, buff=0))
        
        # 2. Backoff -> Sense (БОЛЬШАЯ СТРЕЛКА НАВЕРХ)
        # Идет слева, чтобы не пересекать остальные блоки
        pb1 = b_backoff.get_top()
        x_far_left = pb1[0]+0.3 # Чуть левее блока Backoff
        pb2 = [pb1[0], pb1[1], 0]
        pb3 = [pb1[0], y_high, 0] # Вверх до уровня возврата
        
        path_back = VMobject()
        path_back.set_points_as_corners([pb1, pb2, pb3, p_turn_sense])
        l_ret_back = VGroup(path_back, Arrow(p_turn_sense, p_sense_in, buff=0))

        group = VGroup(
            b_start, t_start, b_sense, t_sense, b_wait_slot, t_wait_slot,
            b_prob, t_prob, 
            b_ack, t_ack, b_backoff, t_backoff, b_success, t_success,
            l1, l_busy, lbl_busy, l_free, lbl_free, l_send, lbl_p, l_wait_prob, lbl_1p,
            l_ack_yes, lbl_yes, l_ack_no, lbl_no,
            l_ret_slot, l_ret_back
        )
        
        steps = {
            "start": b_start, "sense": b_sense, "wait_slot": b_wait_slot,
            "prob": b_prob, "ack": b_ack, "backoff": b_backoff, "success": b_success,
            "arrow_busy": l_busy, "arrow_free": l_free, "arrow_send": l_send, "arrow_wait": l_wait_prob,
            "arrow_ack_yes": l_ack_yes, "arrow_ack_no": l_ack_no,
            "line_return_slot": l_ret_slot, "line_return_back": l_ret_back
        }
        return group, steps