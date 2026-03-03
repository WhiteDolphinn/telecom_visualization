from manim import *
import numpy as np

class PureAlohaAnalysis(Scene):
    def construct(self):
        # 1. Заголовок
        title = Text("Pure Aloha: Интервал уязвимости").scale(1.2).to_edge(UP)
        self.add(title)

        # 2. Создаем линию времени и основной пакет
        timeline = Arrow(start=LEFT * 6, end=RIGHT * 6, color=WHITE)
        self.add(timeline)

        t0_point = LEFT * 1  # Точка начала основного пакета
        packet_width = 2.0   # Это и есть Delta t
        
        # Основной пакет (Packet A)
        packet_a = Rectangle(width=packet_width, height=0.6, fill_opacity=0.8, fill_color=BLUE)
        packet_a.move_to(t0_point + RIGHT * (packet_width / 2) + UP * 0.3)
        
        label_a = Text("Packet A").scale(0.5).move_to(packet_a)
        
        # Появляется пакет А
        self.play(FadeIn(packet_a), Write(label_a))
        self.wait(1)

        # 3. Визуализация интервала уязвимости
        
        # Левая граница уязвимости (t0 - Delta t)
        vulnerability_rect = Rectangle(
            width=packet_width * 2, 
            height=0.6, 
            stroke_opacity=0,
            fill_opacity=0.2, 
            fill_color=RED
        )
        vulnerability_rect.move_to(t0_point + RIGHT * (packet_width/2) + UP*0.3)
        
        # Анимация расширения зоны опасности
        ghost_packet_prev = Rectangle(width=packet_width, height=0.6, fill_opacity=0.3, fill_color=RED)
        ghost_packet_prev.next_to(packet_a, LEFT, buff=0)
        
        ghost_packet_next = Rectangle(width=packet_width, height=0.6, fill_opacity=0.3, fill_color=RED)
        ghost_packet_next.next_to(packet_a, RIGHT, buff=0)
        
        # Рисуем скобку
        brace_line = Line(
            start=packet_a.get_left() - RIGHT * packet_width, 
            end=packet_a.get_right(), 
            color=RED
        ).shift(DOWN * 0.5)
        
        brace = Brace(brace_line, DOWN)
        brace_text = brace.get_text(r"$2 \Delta t$")
        
        self.play(
            FadeIn(ghost_packet_prev),
            run_time=1
        )
        self.play(
            FadeIn(brace),
            Write(brace_text),
            Create(brace_line)
        )
        
        # Пояснение
        explanation = Text("Любое начало передачи в этом окне\nвызовет коллизию", font_size=24, color=RED)
        explanation.next_to(brace, DOWN)
        self.play(Write(explanation))
        self.wait(2)

        # 4. Вывод формул
        self.play(FadeOut(explanation))
        
        math_pos = RIGHT * 3 + UP * 1
        
        eq1 = MathTex(r"P_{success} = P(\text{0 packets in } 2\Delta t)", font_size=36).move_to(math_pos)
        eq2 = MathTex(r"P_{success} = e^{-2 \lambda \Delta t}", font_size=36).next_to(eq1, DOWN)
        eq3 = MathTex(r"S = \lambda \cdot P_{success}", font_size=36).next_to(eq2, DOWN)
        eq4 = MathTex(r"S = \lambda e^{-2 \lambda}", font_size=42, color=YELLOW).next_to(eq3, DOWN, buff=0.5)
        
        # ИСПРАВЛЕНИЕ ЗДЕСЬ:
        # Разбиваем на Text (русский) и MathTex (формула)
        note_text = Text("(при ", font_size=24, color=GRAY)
        note_math = MathTex(r"\Delta t = 1)", font_size=24, color=GRAY)
        
        # Группируем их вместе
        note = VGroup(note_text, note_math).arrange(RIGHT, buff=0.1)
        note.next_to(eq4, RIGHT)

        self.play(Write(eq1))
        self.wait(1)
        self.play(TransformMatchingTex(eq1.copy(), eq2))
        self.wait(1)
        self.play(Write(eq3))
        self.wait(1)
        self.play(Write(eq4), FadeIn(note))
        
        self.wait(3)

# Остальные классы (SlottedAlohaAnalysis и AlohaGraph) остаются без изменений
class SlottedAlohaAnalysis(Scene):
    def construct(self):
        title = Text("Slotted Aloha: Синхронизация").scale(1.2).to_edge(UP)
        self.add(title)

        timeline = Arrow(start=LEFT * 6, end=RIGHT * 6, color=WHITE)
        self.add(timeline)
        
        # Рисуем слоты
        slot_width = 2.0
        slots = VGroup()
        for i in range(-3, 4):
            x = i * slot_width
            line = DashedLine(start=UP*1 + RIGHT*x, end=DOWN*1 + RIGHT*x, color=GRAY)
            slots.add(line)
            
        self.play(Create(slots))
        
        # Пакет А
        packet_a = Rectangle(width=slot_width*0.9, height=0.6, fill_opacity=0.8, fill_color=BLUE)
        packet_a.move_to(RIGHT * (slot_width/2) + UP * 0.3)
        label_a = Text("Packet A").scale(0.5).move_to(packet_a)
        
        self.play(FadeIn(packet_a), Write(label_a))
        
        brace_line = Line(
            start=ORIGIN, 
            end=RIGHT * slot_width, 
            color=BLUE
        ).shift(DOWN * 0.5)
        
        brace = Brace(brace_line, DOWN)
        brace_text = brace.get_text(r"$1 \Delta t$")
        
        self.play(GrowFromCenter(brace), Write(brace_text))
        
        info_text = Text(
            "Коллизия только если другой пакет\nвыберет ЭТОТ ЖЕ слот", 
            font_size=24, color=YELLOW
        ).next_to(brace, DOWN)
        self.play(Write(info_text))
        self.wait(2)
        
        # Формулы
        self.play(FadeOut(info_text))
        
        math_pos = LEFT * 3 + UP * 2
        
        eq1 = MathTex(r"P_{success} = P(\text{0 packets in } 1\Delta t)", font_size=36).move_to(math_pos)
        eq2 = MathTex(r"P_{success} = e^{- \lambda \Delta t}", font_size=36).next_to(eq1, DOWN)
        eq3 = MathTex(r"S = \lambda e^{-\lambda}", font_size=42, color=YELLOW).next_to(eq2, DOWN, buff=0.5)
        
        self.play(Write(eq1))
        self.wait(1)
        self.play(TransformMatchingTex(eq1.copy(), eq2))
        self.wait(1)
        self.play(Write(eq3))
        
        self.wait(3)

class AlohaGraph(Scene):
    def construct(self):
        # Построение осей
        ax = Axes(
            x_range=[0, 3, 0.5],
            y_range=[0, 0.5, 0.1],
            axis_config={"include_tip": False},
            x_length=7,
            y_length=5
        ).add_coordinates()
        
        ax.to_edge(LEFT, buff=1.5)
        
        # Подписи осей через Text
        x_label = Text("Нагрузка G (пакетов / слот)", font_size=24)
        x_label.next_to(ax.x_axis, DOWN, buff=0.3)
        
        y_label = Text("S (пропускная способность)", font_size=24)
        y_label.rotate(PI/2)
        y_label.next_to(ax.y_axis, LEFT, buff=0.3)
        
        self.play(Create(ax), Write(x_label), Write(y_label))
        
        # Графики
        graph_pure = ax.plot(lambda x: x * np.exp(-2 * x), color=RED, x_range=[0, 3])
        label_pure = ax.get_graph_label(graph_pure, "Pure Aloha", x_val=1.0, direction=UP)
        
        graph_slotted = ax.plot(lambda x: x * np.exp(-1 * x), color=BLUE, x_range=[0, 3])
        label_slotted = ax.get_graph_label(graph_slotted, "Slotted Aloha", x_val=2.0, direction=UP)
        
        self.play(Create(graph_pure), Write(label_pure))
        self.wait(1)
        self.play(Create(graph_slotted), Write(label_slotted))
        
        # --- Точки максимума ---
        
        # 1. Pure Aloha
        point_pure = ax.i2gp(0.5, graph_pure) 
        point_axis_pure = ax.c2p(0.5, 0)
        
        dot_pure = Dot(point_pure, color=RED)
        line_pure = DashedLine(start=point_axis_pure, end=point_pure, color=RED_A)
        
        # ВАЖНО: добавлена 'r' перед строкой
        text_pure = MathTex(r"S_{max} \approx 0.18").next_to(dot_pure, UP+RIGHT, buff=0.1).scale(0.7)
        
        # 2. Slotted Aloha
        point_slotted = ax.i2gp(1.0, graph_slotted)
        point_axis_slotted = ax.c2p(1.0, 0)
        
        dot_slotted = Dot(point_slotted, color=BLUE)
        line_slotted = DashedLine(start=point_axis_slotted, end=point_slotted, color=BLUE_A)
        
        # ВАЖНО: добавлена 'r' перед строкой
        text_slotted = MathTex(r"S_{max} \approx 0.37").next_to(dot_slotted, UP+RIGHT, buff=0.1).scale(0.7)
        
        # Анимация
        self.play(FadeIn(dot_pure), Create(line_pure), Write(text_pure))
        self.play(FadeIn(dot_slotted), Create(line_slotted), Write(text_slotted))
        
        self.wait(3)