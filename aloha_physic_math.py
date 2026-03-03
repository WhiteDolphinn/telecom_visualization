from manim import *
import numpy as np

class AlohaMathFinal(Scene):
    def construct(self):
        # --- 1. БЫСТРАЯ НАСТРОЙКА СЦЕНЫ ---
        
        # Левая часть: Физика
        tx1 = self.create_node("Tx 1", color=BLUE).move_to(LEFT * 5.5 + UP * 2)
        tx2 = self.create_node("Tx 2", color=ORANGE).move_to(LEFT * 5.5 + DOWN * 0.5)
        rx = self.create_node("Rx", color=GREY, is_circle=True).move_to(LEFT * 0.5 + UP * 0.75)
        physical_group = VGroup(tx1, tx2, rx)
        
        # Правая часть: Блок-схема
        flow_group, _ = self.create_flowchart()
        flow_group.scale(0.7).to_edge(RIGHT, buff=0.3).shift(UP*0.5)
        flow_title = Text("Алгоритм", font_size=24, color=BLUE).next_to(flow_group, UP)
        
        # Нижняя часть: Временная шкала
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
        label_time = Text("Time (t)", font_size=18).next_to(timeline_axes.x_axis, RIGHT)
        timeline_group = VGroup(timeline_axes, label_row1, label_row2, label_time)

        # Группируем вообще всё
        all_scene_objects = VGroup(physical_group, flow_group, flow_title, timeline_group)
        
        self.add(all_scene_objects)
        
        # --- 2. ПОДГОТОВКА К МАТЕМАТИКЕ ---
        
        t_start_1 = 4.0
        duration = 2.0
        
        rect_width = duration * (timeline_axes.x_length / 10.0)
        
        rect1 = Rectangle(width=rect_width, height=0.6, fill_color=BLUE, fill_opacity=0.6, stroke_width=0)
        rect1.move_to(timeline_axes.c2p(t_start_1, 2), aligned_edge=LEFT)
        self.add(rect1)
        
        self.wait(1)
        
        # --- 3. СДВИГ ЭКРАНА ВНИЗ ---
        
        math_title = Text("Анализ интервала уязвимости", font_size=36).to_edge(UP)
        
        self.play(
            all_scene_objects.animate.shift(DOWN * 1.5), 
            rect1.animate.shift(DOWN * 1.5),
            FadeIn(math_title)
        )
        
        # --- 4. АНИМАЦИЯ ИНТЕРВАЛА УЯЗВИМОСТИ ---
        
        # Призрачный пакет Tx2
        rect2_ghost = Rectangle(
            width=rect_width, 
            height=0.6, 
            fill_color=ORANGE, 
            fill_opacity=0.4, 
            stroke_color=ORANGE,
            stroke_width=2
        )
        rect2_ghost.move_to(timeline_axes.c2p(1.0, 1), aligned_edge=LEFT)
        rect2_ghost.shift(DOWN * 1.5) # Сдвиг из-за анимации камеры
        
        label_ghost = Text("Возможный Tx2", font_size=16, color=ORANGE).next_to(rect2_ghost, UP, buff=0.1)
        label_ghost.add_updater(lambda m: m.next_to(rect2_ghost, UP, buff=0.1))
        
        self.play(FadeIn(rect2_ghost), FadeIn(label_ghost))
        
        # Параметры опасной зоны
        danger_start_t = t_start_1 - duration # 2.0
        danger_end_t = t_start_1 + duration   # 6.0
        shift_vec = DOWN * 1.5
        
        danger_start_point = timeline_axes.c2p(danger_start_t, 1) + shift_vec
        
        danger_line = Line(
            start=danger_start_point,
            end=danger_start_point + RIGHT*0.01,
            color=RED,
            stroke_width=10
        )
        self.add(danger_line)
        
        # Движение 1
        target_pos_start = timeline_axes.c2p(danger_start_t, 1) + shift_vec
        self.play(
            rect2_ghost.animate.move_to(target_pos_start, aligned_edge=LEFT),
            run_time=1.5
        )
        
        collision_text = Text("Начало коллизии", color=RED, font_size=20).next_to(rect2_ghost, DOWN)
        self.play(FadeIn(collision_text))
        self.wait(0.5)
        self.play(FadeOut(collision_text))
        
        # Updater
        def update_danger_line(mob):
            current_x = rect2_ghost.get_left()[0]
            start_x = danger_start_point[0]
            y = danger_start_point[1]
            z = 0
            
            if current_x < start_x: current_x = start_x + 0.01
                
            mob.put_start_and_end_on(
                danger_start_point, 
                np.array([current_x, y, z])
            )

        danger_line.add_updater(update_danger_line)
        
        # Движение 2
        target_pos_end = timeline_axes.c2p(danger_end_t, 1) + shift_vec
        
        self.play(
            rect2_ghost.animate.move_to(target_pos_end, aligned_edge=LEFT),
            rect1.animate.set_color(RED),
            run_time=4.0,
            rate_func=linear
        )
        
        danger_line.remove_updater(update_danger_line)
        
        collision_text.text = "Конец коллизии"
        collision_text.next_to(rect2_ghost, DOWN)
        self.play(FadeIn(collision_text))
        self.wait(0.5)
        self.play(FadeOut(collision_text), rect1.animate.set_color(BLUE))
        
        self.play(FadeOut(rect2_ghost), FadeOut(label_ghost))
        
        # --- 5. ВЫВОД ФОРМУЛ (ИСПРАВЛЕНО) ---
        
        # 1. Первая скобка (Интервал уязвимости)
        p_left = danger_start_point
        p_right = timeline_axes.c2p(danger_end_t, 1) + shift_vec
        brace = Brace(Line(p_left, p_right), UP, buff=0.1)
        
        # ИСПОЛЬЗУЕМ VGROUP вместо get_text, чтобы смешать Text и MathTex
        b_lbl_text = Text("Интервал уязвимости =", font_size=18)
        b_lbl_math = MathTex(r"2 \cdot T", font_size=24)
        brace_text = VGroup(b_lbl_text, b_lbl_math).arrange(RIGHT, buff=0.1).next_to(brace, UP)
        
        # 2. Вторая скобка (Длительность T)
        p_p1_left = timeline_axes.c2p(t_start_1, 2) + shift_vec
        p_p1_right = timeline_axes.c2p(t_start_1 + duration, 2) + shift_vec
        brace_pkt = Brace(Line(p_p1_left, p_p1_right), UP, buff=0.1)
        
        b_pkt_text = Text("Длительность", font_size=18)
        b_pkt_math = MathTex("T", font_size=24)
        brace_pkt_label = VGroup(b_pkt_text, b_pkt_math).arrange(RIGHT, buff=0.1).next_to(brace_pkt, UP)
        
        self.play(
            GrowFromCenter(brace), Write(brace_text),
            GrowFromCenter(brace_pkt), Write(brace_pkt_label)
        )
        
        # 3. Формулы
        # Собираем строки вручную из Text и MathTex
        
        # Строка 1: Вероятность успеха ...
        row1_text = Text("Вероятность успеха:", font_size=24)
        row1_math = MathTex(r"P_{succ} = e^{-2 \lambda T}", font_size=30)
        row1 = VGroup(row1_text, row1_math).arrange(RIGHT, buff=0.2)
        
        # Строка 2: Пропускная способность ...
        row2_text = Text("Пропускная способность:", font_size=24)
        row2_math = MathTex(r"S = G \cdot e^{-2G}", font_size=30)
        row2 = VGroup(row2_text, row2_math).arrange(RIGHT, buff=0.2)
        
        formulas = VGroup(row1, row2).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        formulas.move_to(UP * 2.5) 
        
        self.play(Write(formulas))
        
        # Рамка вокруг формулы S
        box = SurroundingRectangle(row2, color=YELLOW, buff=0.15)
        self.play(Create(box))
        
        self.wait(3)

    # --- ВСПОМОГАТЕЛЬНЫЕ ---
    def create_node(self, label, color=BLUE, is_circle=False):
        if is_circle:
            shape = Circle(radius=0.4, fill_color=color, fill_opacity=0.2, stroke_color=color)
        else:
            shape = Square(side_length=0.8, fill_color=color, fill_opacity=0.2, stroke_color=color)
        label_obj = Text(label, font_size=20).move_to(shape)
        line = Line(UP*0.4, UP*0.7).move_to(shape.get_top() + UP*0.1)
        arc = Arc(radius=0.2, start_angle=PI/4, angle=PI/2).move_arc_center_to(line.get_end()+DOWN*0.1)
        return VGroup(shape, label_obj, line, arc)

    def create_flowchart(self):
        w = 2.0
        b_start = Rectangle(width=w, height=0.5, stroke_color=GREY)
        b_send = Rectangle(width=w, height=0.5, stroke_color=GREY).next_to(b_start, DOWN, buff=0.4)
        group = VGroup(b_start, b_send)
        return group, {}