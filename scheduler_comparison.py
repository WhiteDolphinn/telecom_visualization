from manim import *
import random

class SchedulerComparison(Scene):
    def construct(self):
        # --- НАСТРОЙКА ЛЕЙАУТА ---
        main_title = Text("Планировщики", font_size=32).to_edge(UP, buff=0.1)
        self.add(main_title)

        # 1. ПОЛЬЗОВАТЕЛИ
        u1_grp = self.create_user("U1", 12, GREEN).to_edge(LEFT, buff=0.5).shift(UP*2)
        u2_grp = self.create_user("U2", 6, YELLOW).to_edge(LEFT, buff=0.5)
        u3_grp = self.create_user("U3", 2, RED).to_edge(LEFT, buff=0.5).shift(DOWN*2)
        
        users = [u1_grp, u2_grp, u3_grp]
        colors = [GREEN, YELLOW, RED]
        self.add(*users)

        right_panel_center = RIGHT * 0.5

        # ============================================================
        # ПОДГОТОВКА СЕТКИ (12 СЛОТОВ)
        # ============================================================
        grid_group, grid_cells = self.create_strip_grid(12)
        grid_group.to_edge(DOWN, buff=0.5)
        self.add(grid_group)

        # ============================================================
        # ЧАСТЬ 2: MAX RATE (8 СЛОТОВ)
        # ============================================================
        algo_title = Text("1. Max Rate", font_size=28, color=BLUE).next_to(main_title, DOWN)
        formula = MathTex(r"M_k = R_k(t)").next_to(algo_title, DOWN, buff=0.1)
        self.play(Write(algo_title), Write(formula))

        headers_mr = VGroup(
            Text("User", font_size=32), MathTex(r"R_k(t)", font_size=32), MathTex(r"M_k", font_size=28)
        ).arrange(RIGHT, buff=1.0).move_to(right_panel_center).shift(UP)
        self.play(FadeIn(headers_mr))

        # Симуляция 8 слотов (U1 всегда выигрывает)
        for t in range(8):
            rates = [int(random.uniform(11, 13)), int(random.uniform(5, 7)), int(random.uniform(1, 3))]
            rows, row_objs = self.create_rows_max_rate(headers_mr, rates, colors)
            self.add(rows)
            self.wait(0.3) # Быстро

            win_idx = 0 # Всегда U1
            
            box = SurroundingRectangle(row_objs[win_idx], color=YELLOW, buff=0.05)
            self.play(Create(box), run_time=0.3)
            self.play(grid_cells[t].animate.set_fill(colors[win_idx], opacity=0.8), run_time=0.3)
            self.remove(rows, box)

        self.play(FadeOut(algo_title), FadeOut(formula), FadeOut(headers_mr), *[c.animate.set_fill(opacity=0) for c in grid_cells])

        # ============================================================
        # ЧАСТЬ 1: ФИЗИКА КАНАЛА
        # ============================================================
        phys_title = Text("Почему меняется R(t)?", font_size=24, color=YELLOW).next_to(main_title, DOWN)
        self.play(FadeIn(phys_title))

        ax = Axes(x_range=[0, 10], y_range=[0, 15], x_length=8, y_length=5, axis_config={"include_tip": False}).move_to(right_panel_center)
        x_label = Text("Время", font_size=16).next_to(ax.x_axis, DOWN, buff=0.2)
        y_label = Text("SNR / Скорость / R(t)", font_size=16).rotate(PI/2).next_to(ax.y_axis, LEFT, buff=0.2)
        labels = VGroup(x_label, y_label)
        
        curve1 = ax.plot(lambda x: 12 + 1.5*np.sin(x) + np.random.normal(0, 0.5), color=GREEN)
        lbl_c1 = Text("U1: Хороший канал", font_size=16, color=GREEN).next_to(curve1, 0.5*UP).shift(LEFT*2)
        curve3 = ax.plot(lambda x: 2 + 0.8*np.sin(x*2) + np.random.normal(0, 0.3), color=RED)
        lbl_c3 = Text("U3: Плохой канал", font_size=16, color=RED).next_to(curve3, UP)

        
        explanation = Text("Канальные условия не являются постоянными во времени", font_size=16).next_to(lbl_c3, 2*UP, buff=0.5)
        # self.play(Write(explanation))
        self.play(Create(ax), Write(labels), Create(curve1), Write(lbl_c1), Create(curve3), Write(lbl_c3), Write(explanation))
        self.wait(1)
        
        self.play(FadeOut(ax), FadeOut(labels), FadeOut(curve1), FadeOut(curve3), FadeOut(lbl_c1), FadeOut(lbl_c3), FadeOut(phys_title), FadeOut(explanation))



        # ============================================================
        # ЧАСТЬ 3: PROPORTIONAL FAIR (СЦЕНАРИЙ)
        # ============================================================
        algo_title = Text("3. Proportional Fair (PF)", font_size=28, color=BLUE).next_to(main_title, DOWN)
        formula = MathTex(r"M_k = \frac{R_k(t)}{\bar{R}_k(t)}").next_to(algo_title, DOWN, buff=0.1)
        self.play(Write(algo_title), Write(formula))

        # Пояснительные стрелки
        # dummy_header = VGroup(MathTex(r"R_k(t)", font_size=24), MathTex(r"\bar{R}_k(t)", font_size=24)).arrange(RIGHT, buff=1.5).move_to(right_panel_center).shift(UP)
        ar1 = Arrow(start=RIGHT, end=LEFT, color=YELLOW).next_to(formula, RIGHT).shift(0.35*UP)
        ar2 = Arrow(start=DOWN, end=UP, color=ORANGE).next_to(formula, DOWN).shift(0.6*RIGHT)
        t1 = Text("Текущая, вычисляется из графика 1", font_size=18, color=YELLOW).next_to(ar1, DOWN).shift(1.8*RIGHT)
        t2 = Text("Фактическая, вычисляется с помощью усреднения по окну и\nучитывает наличие/отсутствие передачи в данном слоте", font_size=18, color=ORANGE).next_to(ar2, DOWN)
        
        self.play( GrowArrow(ar1), Write(t1), GrowArrow(ar2), Write(t2))
        self.wait(2)
        self.play(FadeOut(ar1), FadeOut(t1), FadeOut(ar2), FadeOut(t2))

        headers_pf = VGroup(
            Text("User", font_size=32), MathTex(r"R_k(t)", font_size=32), MathTex(r"\bar{R}_k(t)", font_size=32), Text("M", font_size=32)
        ).arrange(RIGHT, buff=0.5).move_to(right_panel_center).shift(UP)
        self.play(FadeIn(headers_pf))

        rkt = MathTex(r"\bar{R}_k(t) = (1-\alpha) \cdot \bar{R}_k(t-1) + \alpha \cdot R_k(t) \cdot \mathbb{I}(transmission)", font_size=32).next_to(grid_group, UP)
        self.play(Write(rkt))

        # --- СЦЕНАРИЙ (HARDCODED) ---
        # Мы хотим показать: U1 берет много, но U2 и U3 иногда проскакивают
        avg_rates = [12.0, 6.0, 2.0] 
        alpha = 0.2

        # Список скоростей R(t) для каждого слота. 
        # Подбираем так, чтобы метрика U1 была часто выше, но иногда ниже.
        # Avg ~ 12, 6, 2.
        # Если R = [12, 6, 2] -> M = [1, 1, 1].
        # Чтобы выиграл U3 (Red), ему нужно R=4 (M=2.0), а U1 R=10 (M=0.8).
        
        scenario_rates = [
            [13, 6, 2], # U1 Win (1.08 vs 1.0 vs 1.0)
            [14, 5, 1], # U1 Win (High peak)
            [12, 7, 2], # U1 Win (Still strong)
            [10, 8, 2], # U2 Win! (U2 spike: 8/6=1.33 > U1 10/12=0.8)
            [13, 6, 2], # U1 Back
            [13, 6, 2], # U1 Again
            [11, 5, 4], # U3 Win! (U3 spike: 4/2=2.0 > U1 0.9)
            [14, 6, 2], # U1 Back
            [13, 6, 2], # U1
        ]

        for t in range(len(scenario_rates)):
            rates = scenario_rates[t]
            metrics = [round(rates[i]/avg_rates[i], 2) for i in range(3)]
            
            rows, row_objs, avg_txt_objs = self.create_rows_pf(headers_pf, rates, avg_rates, metrics, colors)
            self.add(rows)
            self.wait(1)

            win_idx = metrics.index(max(metrics))
            
            box = SurroundingRectangle(row_objs[win_idx], color=YELLOW, buff=0.05)
            self.play(Create(box), run_time=0.1)
            
            target_cell = grid_cells[t]
            self.play(target_cell.animate.set_fill(colors[win_idx], opacity=0.8), run_time=0.2)

            # Анимация +R -> Avg
            plus_r = Text(f"+{rates[win_idx]}", font_size=16, color=colors[win_idx]).move_to(target_cell)
            self.play(plus_r.animate.move_to(avg_txt_objs[win_idx]).scale(0.5), run_time=0.9)
            self.remove(plus_r)

            # Обновление средних
            for i in range(3):
                val = rates[i] if i == win_idx else 0 # В формуле PF обычно обновляется только победитель или через экспоненту
                # Упрощенная формула визуализации: Победитель обновляется активно, проигравшие деградируют
                if i == win_idx:
                    avg_rates[i] = (1-alpha)*avg_rates[i] + alpha*rates[i]
                else:
                    avg_rates[i] = (1-alpha)*avg_rates[i] # decay
            
            self.play(
                avg_txt_objs[win_idx].animate.set_value(avg_rates[win_idx]).set_color(WHITE).scale(1.2),
                *[avg_txt_objs[i].animate.set_value(avg_rates[i]).set_color(GRAY).scale(0.9) for i in range(3) if i != win_idx],
                run_time=0.9
            )
            self.play(avg_txt_objs[win_idx].animate.scale(1/1.2).set_color(GRAY), *[avg_txt_objs[i].animate.scale(1/0.9) for i in range(3) if i != win_idx], run_time=0.3)
            
            self.remove(rows, box)

        self.play(FadeOut(rkt))
        conc = Text("В случае насыщенного трафика все получают\nодинаковое число ресурсных блоков.", font_size=20).next_to(grid_group, UP)
        self.play(Write(conc))
        self.wait(2)

        self.play(FadeOut(algo_title), FadeOut(formula), FadeOut(headers_pf), FadeOut(conc), *[c.animate.set_fill(opacity=0) for c in grid_cells])

        # ============================================================
        # ЧАСТЬ 4: QoS (DELAY)
        # ============================================================
        algo_title = Text("4. Упрощенный M-LWDF", font_size=28, color=BLUE).next_to(main_title, DOWN)
        formula = MathTex(r"M_k = R_k(t) \cdot \text{Delay}_k").next_to(algo_title, DOWN, buff=0.1)
        self.play(Write(algo_title), Write(formula))

        headers_qos = VGroup(
            Text("User", font_size=24), MathTex("R_k(t)", font_size=32), Text("Delay", font_size=24), Text("M", font_size=24)
        ).arrange(RIGHT, buff=0.6).move_to(right_panel_center).shift(UP)
        self.play(FadeIn(headers_qos))

        delays = [10, 20, 150] 

        for t in range(8):
            rates = [int(random.uniform(10, 13)), int(random.uniform(5, 8)), int(random.uniform(1, 4))]
            metrics = [int(rates[i] * delays[i]) for i in range(3)]
            rows, row_objs, delay_txt_objs = self.create_rows_qos(headers_qos, rates, delays, metrics, colors)
            self.add(rows)
            self.wait(1.0)

            win_idx = metrics.index(max(metrics))
            box = SurroundingRectangle(row_objs[win_idx], color=YELLOW, buff=0.05)
            self.play(Create(box), run_time=0.1)
            self.play(grid_cells[t].animate.set_fill(colors[win_idx], opacity=0.8), run_time=0.5)

            delays[win_idx] = 0
            for i in range(3):
                if i != win_idx: delays[i] += 50
            
            self.play(delay_txt_objs[win_idx].animate.set_value(0).set_color(GREEN), run_time=0.5)
            self.remove(rows, box)

        self.wait(2)

    # --- HELPER FUNCTIONS ---
    def create_user(self, name, speed_hint, color):
        grp = VGroup(
            Square(side_length=0.6, color=color, fill_opacity=0.5),
            Text(name, font_size=16).next_to(Square(side_length=0.6), UP, buff=0.1),
            Text(f"~{speed_hint} Mbps", font_size=18).next_to(Square(side_length=0.6), DOWN, buff=0.1)
        )
        return grp

    def create_strip_grid(self, cols):
        cells = []
        grp = VGroup()
        label = Text("Назначаем пользователю с наибольшим M:", font_size=20).move_to(LEFT * 6)
        grp.add(label)
        for i in range(cols):
            sq = Square(side_length=0.5, color=GRAY, stroke_width=2)
            if i == 0: sq.next_to(label, RIGHT, buff=0.5)
            else: sq.next_to(cells[-1], RIGHT, buff=0.1)
            num = Text(str(i+1), font_size=16, color=GRAY).move_to(sq)
            grp.add(sq, num)
            cells.append(sq)
        grp.center()
        return grp, cells

    def create_rows_max_rate(self, headers, rates, colors):
        grp = VGroup()
        row_objs = []
        for i in range(3):
            y_pos = headers.get_center()[1] - 0.7 - i*0.7
            t_name = Text(f"U{i+1}", font_size=28, color=colors[i]).move_to([headers[0].get_x(), y_pos, 0])
            t_rate = Integer(rates[i], font_size=32).move_to([headers[1].get_x(), y_pos, 0])
            t_metr = Integer(rates[i], font_size=32).move_to([headers[2].get_x(), y_pos, 0])
            row = VGroup(t_name, t_rate, t_metr)
            grp.add(row)
            row_objs.append(row)
        return grp, row_objs

    def create_rows_pf(self, headers, rates, avgs, metrics, colors):
        grp = VGroup()
        row_objs = []
        avg_objs = []
        for i in range(3):
            y_pos = headers.get_center()[1] - 0.7 - i*0.7
            t_name = Text(f"U{i+1}", font_size=28, color=colors[i]).move_to([headers[0].get_x(), y_pos, 0])
            t_inst = Integer(rates[i], font_size=32).move_to([headers[1].get_x(), y_pos, 0])
            t_avg  = DecimalNumber(avgs[i], num_decimal_places=1, font_size=32).move_to([headers[2].get_x(), y_pos, 0])
            t_metr = DecimalNumber(metrics[i], num_decimal_places=2, font_size=32).move_to([headers[3].get_x(), y_pos, 0])
            row = VGroup(t_name, t_inst, t_avg, t_metr)
            grp.add(row)
            row_objs.append(row)
            avg_objs.append(t_avg)
        return grp, row_objs, avg_objs

    def create_rows_qos(self, headers, rates, delays, metrics, colors):
        grp = VGroup()
        row_objs = []
        delay_objs = []
        for i in range(3):
            y_pos = headers.get_center()[1] - 0.7 - i*0.7
            t_name = Text(f"U{i+1}", font_size=28, color=colors[i]).move_to([headers[0].get_x(), y_pos, 0])
            t_rate = Integer(rates[i], font_size=32).move_to([headers[1].get_x(), y_pos, 0])
            d_col = RED if delays[i] > 100 else WHITE
            t_delay = Integer(delays[i], font_size=32, color=d_col).move_to([headers[2].get_x(), y_pos, 0])
            t_metr = Integer(metrics[i], font_size=32).move_to([headers[3].get_x(), y_pos, 0])
            row = VGroup(t_name, t_rate, t_delay, t_metr)
            grp.add(row)
            row_objs.append(row)
            delay_objs.append(t_delay)
        return grp, row_objs, delay_objs