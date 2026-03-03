from manim import *

class AlohaFlowchart(Scene):
    def construct(self):
        # --- НАСТРОЙКА СЦЕНЫ ---
        
        # 1. Физический мир (Слева)
        # Иконка роутера (упрощенная)
        router_body = RoundedRectangle(corner_radius=0.1, height=0.5, width=1, fill_color=BLUE_E, fill_opacity=1).set_stroke(WHITE, 2)
        router_ant = Line(start=router_body.get_top(), end=router_body.get_top() + UP*0.3)
        router = VGroup(router_body, router_ant).move_to(LEFT * 5 + UP * 0.5)
        router_label = Text("Наш Роутер", font_size=20).next_to(router, DOWN)
        
        # Иконка сервера
        server = Circle(radius=0.4, fill_color=GREY, fill_opacity=1).set_stroke(WHITE, 2).move_to(LEFT * 1 + UP * 0.5)
        server_label = Text("Сервер", font_size=20).next_to(server, DOWN)
        
        physical_world = VGroup(router, router_label, server, server_label)
        
        # Разделительная линия
        separator = Line(UP*3.5, DOWN*3.5).move_to(LEFT * 2.5)
        
        # 2. Логический мир (Блок-схема Справа)
        # Координаты для блоков
        x_flow = 3.5
        y_start = 2.5
        gap = 1.5
        
        # Блок "Старт / Есть пакет"
        box_start = Rectangle(width=3.5, height=0.8, color=WHITE).move_to(RIGHT*x_flow + UP*y_start)
        txt_start = Text("Есть пакет для отправки", font_size=20).move_to(box_start)
        group_start = VGroup(box_start, txt_start)
        
        # Блок "Отправка"
        box_send = Rectangle(width=3.5, height=0.8, color=WHITE).move_to(RIGHT*x_flow + UP*(y_start - gap))
        txt_send = Text("Отправить пакет", font_size=20).move_to(box_send)
        group_send = VGroup(box_send, txt_send)
        
        # Блок "Решение" (Ромб)
        box_decision = Polygon(
            UP, RIGHT*2, DOWN, LEFT*2, color=WHITE
        ).scale(0.5).move_to(RIGHT*x_flow + UP*(y_start - gap*2))
        txt_decision = Text("Получен ACK?", font_size=20).move_to(box_decision)
        group_decision = VGroup(box_decision, txt_decision)
        
        # Блок "Успех" (Вниз)
        box_success = Rectangle(width=3.5, height=0.8, color=GREEN).move_to(RIGHT*x_flow + UP*(y_start - gap*3))
        txt_success = Text("Успех (Готово)", font_size=20).move_to(box_success)
        group_success = VGroup(box_success, txt_success)
        
        # Блок "Ожидание" (Слева от решения)
        box_wait = Rectangle(width=2.5, height=0.8, color=RED).move_to(RIGHT*(x_flow - 3.5) + UP*(y_start - gap*2))
        txt_wait = Text("Ждать Random Time", font_size=18).move_to(box_wait)
        group_wait = VGroup(box_wait, txt_wait)
        
        # Стрелки
        arrow1 = Arrow(start=box_start.get_bottom(), end=box_send.get_top(), buff=0)
        arrow2 = Arrow(start=box_send.get_bottom(), end=box_decision.get_top(), buff=0)
        
        # Стрелка Да (вниз)
        arrow_yes = Arrow(start=box_decision.get_bottom(), end=box_success.get_top(), buff=0)
        lbl_yes = Text("Да", font_size=16, color=GREEN).next_to(arrow_yes, RIGHT, buff=0.1)
        
        # Стрелка Нет (влево)
        arrow_no = Arrow(start=box_decision.get_left(), end=box_wait.get_right(), buff=0)
        lbl_no = Text("Нет (Timeout)", font_size=16, color=RED).next_to(arrow_no, UP, buff=0.1)
        
        # Стрелка возврата (от Wait к Send)
        # Рисуем ломаную линию
        path_return = VMobject()
        p1 = box_wait.get_top()
        p2 = p1 + UP * 0.8
        p3 = box_send.get_left()
        path_return.set_points_as_corners([p1, p2, [p3[0], p2[1], 0], p3])
        arrow_return = Arrow(start=path_return.get_points()[-2], end=p3, buff=0)
        line_return = VGroup(path_return, arrow_return).set_color(WHITE)
        
        flowchart = VGroup(
            group_start, arrow1, 
            group_send, arrow2, 
            group_decision, arrow_yes, lbl_yes, group_success,
            arrow_no, lbl_no, group_wait, line_return
        )
        
        # --- АНИМАЦИЯ ---
        
        self.play(FadeIn(physical_world), Create(separator))
        self.play(Write(flowchart))
        self.wait(1)
        
        # Вспомогательная функция подсветки активного блока
        def highlight_step(group, color=YELLOW, scale=1.1):
            box = group[0]
            self.play(
                box.animate.set_stroke(color, 4),
                group.animate.scale(scale),
                run_time=0.5
            )
            return box

        def unhighlight_step(group, scale=1.1): # scale должен быть таким же, чтобы вернуть обратно
            box = group[0]
            self.play(
                box.animate.set_stroke(WHITE, 1),
                group.animate.scale(1/scale),
                run_time=0.3
            )

        # СЦЕНАРИЙ 1: КОЛЛИЗИЯ И ПОВТОР
        
        # 1. Start
        highlight_step(group_start)
        self.wait(0.5)
        unhighlight_step(group_start)
        
        # 2. Send
        highlight_step(group_send)
        
        # Анимация пакета (синий)
        packet = Dot(color=BLUE, radius=0.15).move_to(router.get_center())
        self.add(packet)
        self.play(packet.animate.move_to(server.get_center()), run_time=1.5)
        
        # Внезапная коллизия! (Прилетает красный пакет "врага")
        enemy_packet = Dot(color=RED, radius=0.15).move_to(server.get_center() + UP*2)
        self.add(enemy_packet)
        self.play(enemy_packet.animate.move_to(server.get_center()), run_time=0.2)
        
        # Взрыв
        flash = Flash(server.get_center(), color=RED, flash_radius=0.5)
        lbl_bang = Text("Коллизия!", color=RED, font_size=24).next_to(server, UP)
        self.play(flash, FadeIn(lbl_bang), FadeOut(packet), FadeOut(enemy_packet))
        
        unhighlight_step(group_send)
        
        # 3. Decision (Нет ACK)
        highlight_step(group_decision)
        self.wait(1)
        # Показываем, что идем влево
        self.play(Indicate(arrow_no, color=RED))
        self.play(FadeOut(lbl_bang))
        unhighlight_step(group_decision)
        
        # 4. Wait Random Time
        highlight_step(group_wait, color=RED)
        
        # Таймер
        timer_val = ValueTracker(2.0)
        timer_text = DecimalNumber(2.0, num_decimal_places=1, color=RED).next_to(box_wait, DOWN)
        self.add(timer_text)
        timer_text.add_updater(lambda d: d.set_value(timer_val.get_value()))
        
        self.play(timer_val.animate.set_value(0), run_time=2, rate_func=linear)
        self.remove(timer_text)
        
        unhighlight_step(group_wait)
        
        # Возврат к отправке
        self.play(ShowPassingFlash(line_return.copy().set_color(YELLOW), run_time=1))
        
        # СЦЕНАРИЙ 2: УСПЕХ
        
        # 5. Send Again
        highlight_step(group_send)
        
        packet_retry = Dot(color=BLUE, radius=0.15).move_to(router.get_center())
        self.add(packet_retry)
        self.play(packet_retry.animate.move_to(server.get_center()), run_time=1.5)
        
        # Сервер стал зеленым (принял)
        self.play(server.animate.set_fill(GREEN))
        
        unhighlight_step(group_send)
        
        # 6. Decision (Есть ACK)
        highlight_step(group_decision)
        
        # ACK летит обратно
        ack_packet = Text("ACK", font_size=14, color=GREEN).move_to(server.get_center())
        self.play(ack_packet.animate.move_to(router.get_center()), run_time=1)
        self.play(FadeOut(ack_packet))
        
        self.play(Indicate(arrow_yes, color=GREEN))
        unhighlight_step(group_decision)
        
        # 7. Success
        highlight_step(group_success, color=GREEN)
        self.play(Indicate(group_success))
        
        self.wait(3)