from manim import *

# Вспомогательная функция для создания иконки роутера
def create_router_icon():
    body = RoundedRectangle(corner_radius=0.05, height=0.25, width=0.5, fill_opacity=1, fill_color=BLUE_E).set_stroke(WHITE, 2)
    antenna = Line(start=body.get_top(), end=body.get_top() + UP * 0.25, stroke_width=2)
    
    # Волны сигнала
    arc1 = Arc(radius=0.1, angle=PI/2, start_angle=PI/4, arc_center=antenna.get_end() + DOWN*0.05).set_stroke(WHITE, 2)
    arc2 = Arc(radius=0.2, angle=PI/2, start_angle=PI/4, arc_center=antenna.get_end() + DOWN*0.05).set_stroke(WHITE, 2)
    
    icon = VGroup(body, antenna, arc1, arc2)
    return icon

class AlohaBase(Scene):
    def construct_timeline(self, num_nodes=4, length=10):
        # Группа для всех элементов
        self.axes_group = VGroup()
        self.timelines = []
        self.routers = []
        
        start_y = 2
        gap = 1.5
        
        for i in range(num_nodes):
            y_pos = start_y - i * gap
            
            # Роутер
            router = create_router_icon()
            router.move_to(LEFT * 5 + UP * y_pos)
            
            # Линия времени
            line = Arrow(start=LEFT * 4, end=RIGHT * 5, buff=0, color=WHITE)
            line.move_to(UP * (y_pos - 0.15) + RIGHT * 0.5) # Смещение относительно роутера
            
            self.routers.append(router)
            self.timelines.append(line)
            self.axes_group.add(router, line)
            
        self.play(FadeIn(self.axes_group))

    def create_packet(self, node_index, start_time, duration, color=BLUE):
        # start_time от 0 до 1 (относительно длины линии)
        timeline = self.timelines[node_index]
        line_start = timeline.get_start()[0]
        line_length = timeline.get_length()
        
        # Вычисляем позицию
        pos_x = line_start + (start_time * line_length)
        packet_width = duration * line_length * 0.1 # Масштабирование ширины
        
        packet = Rectangle(width=packet_width, height=0.4, fill_opacity=0.7, fill_color=color)
        packet.set_stroke(WHITE, 1)
        # Выравниваем левый край пакета по времени старта
        packet.move_to([pos_x + packet_width/2, timeline.get_y() + 0.25, 0])
        
        return packet, pos_x, pos_x + packet_width

class PureAloha(AlohaBase):
    def construct(self):
        # Заголовок
        title = Text("Pure Aloha").scale(1.5).to_edge(UP+LEFT)
        self.add(title)
        
        # Создаем таймлайны
        self.construct_timeline(num_nodes=4)
        
        # Данные пакетов: (индекс_ноды, время_старта, длительность)
        # Время старта берем условно от 0.0 до 1.0 (вдоль стрелки)
        packet_data = [
            (0, 0.05, 1.5), # Пакет 1 (верхний)
            (1, 0.25, 1.5), # Пакет 2 (перекрывается)
            (2, 0.35, 1.5), # Пакет 3 (перекрывается)
            (2, 0.75, 1.5), # Пакет 4 (успешный)
            (3, 0.55, 1.5), # Пакет 5 (успешный)
        ]
        
        packets_mobjects = []
        ranges = []
        
        # Рисуем пакеты
        for p_info in packet_data:
            node_idx, start, dur = p_info
            pkt, start_x, end_x = self.create_packet(node_idx, start, dur)
            packets_mobjects.append(pkt)
            ranges.append({'mobject': pkt, 'start': start_x, 'end': end_x, 'row': node_idx})
        
        self.play(LaggedStart(*[Create(p) for p in packets_mobjects], lag_ratio=0.5))
        
        # Логика поиска коллизий
        collisions = []
        for i in range(len(ranges)):
            for j in range(i + 1, len(ranges)):
                r1 = ranges[i]
                r2 = ranges[j]
                
                # Проверка пересечения отрезков времени [start, end]
                # max(start1, start2) < min(end1, end2)
                overlap_start = max(r1['start'], r2['start'])
                overlap_end = min(r1['end'], r2['end'])
                
                if overlap_start < overlap_end:
                    # Найдена коллизия
                    collisions.append((r1, r2, overlap_start, overlap_end))

        # Визуализация коллизий
        collision_anims = []
        for r1, r2, o_start, o_end in collisions:
            # Красный прямоугольник на пересечении для первого пакета
            col_rect1 = Rectangle(width=o_end - o_start, height=0.4, fill_opacity=1, fill_color=RED)
            col_rect1.move_to([o_start + (o_end - o_start)/2, r1['mobject'].get_y(), 0])
            col_rect1.set_stroke(opacity=0)
            
            # Красный прямоугольник на пересечении для второго пакета
            col_rect2 = col_rect1.copy().move_to([o_start + (o_end - o_start)/2, r2['mobject'].get_y(), 0])
            
            collision_anims.append(FadeIn(col_rect1))
            collision_anims.append(FadeIn(col_rect2))
            
            # Вертикальные пунктирные линии границ коллизии (как на картинке)
            dash_line1 = DashedLine(
                start=UP*2.5 + RIGHT*o_start, 
                end=DOWN*3.5 + RIGHT*o_start, 
                dash_length=0.1
            ).set_opacity(0.5)
            
            dash_line2 = DashedLine(
                start=UP*2.5 + RIGHT*o_end, 
                end=DOWN*3.5 + RIGHT*o_end, 
                dash_length=0.1
            ).set_opacity(0.5)
            
            collision_anims.append(Create(dash_line1))
            collision_anims.append(Create(dash_line2))

        if collision_anims:
            self.play(*collision_anims)
            
            # Текст и стрелка
            # Берем координаты первой коллизии для примера
            _, _, c_start, c_end = collisions[0]
            center_x = c_start + (c_end - c_start)/2
            
            arrow = Arrow(start=UP*2 + RIGHT*(center_x+1.5), end=UP*0.5 + RIGHT*center_x, color=BLUE_A)
            text_col = Text("Коллизия\nоба пакета\nпотеряны", font_size=24, color=RED)
            text_col.next_to(arrow.get_start(), UP)
            
            self.play(GrowArrow(arrow), Write(text_col))
        
        self.wait(2)

class SlottedAloha(AlohaBase):
    def construct(self):
        title = Text("Slotted Aloha").scale(1.5).to_edge(UP+LEFT)
        self.add(title)
        
        self.construct_timeline(num_nodes=4)
        
        # Рисуем слоты (вертикальные линии)
        # Получаем границы первой линии времени для координат
        timeline_ref = self.timelines[0]
        start_x = timeline_ref.get_start()[0]
        end_x = timeline_ref.get_end()[0]
        total_width = end_x - start_x
        
        num_slots = 6
        slot_width = total_width / num_slots
        
        slots = VGroup()
        for i in range(num_slots + 1):
            x = start_x + i * slot_width
            line = DashedLine(start=UP*2.5 + RIGHT*x, end=DOWN*3.5 + RIGHT*x, color=GRAY)
            slots.add(line)
            
        self.play(Create(slots))
        
        # Данные пакетов. В Slotted Aloha время старта дискретное (по слотам)
        # Формат: (индекс_ноды, номер_слота)
        packet_slots = [
            (0, 0), # Слот 0
            (1, 1), # Слот 1 (коллизия)
            (2, 1), # Слот 1 (коллизия)
            (3, 3), # Слот 3 (успех)
            (1, 4), # Слот 4 (успех)
        ]
        
        packets = []
        collisions_indices = []
        
        # Определяем, какие слоты имеют коллизии
        from collections import Counter
        slot_counts = Counter([s for _, s in packet_slots])
        
        for node_idx, slot_idx in packet_slots:
            # Создаем пакет
            # Время старта нормализовано 0..1
            start_norm = (slot_idx * slot_width) / total_width
            # Длительность чуть меньше слота для красоты
            duration_norm = 0.9 * (1.0 / num_slots) * 10 # *10 чтобы компенсировать делитель в create_packet
            
            color = RED if slot_counts[slot_idx] > 1 else BLUE
            
            pkt, _, _ = self.create_packet(node_idx, start_norm, duration_norm, color)
            packets.append(pkt)
            
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN*0.2) for p in packets], lag_ratio=0.3))
        
        # Пояснение
        text_info = Text("Пакеты синхронизированы\nпо слотам", font_size=24, color=WHITE)
        text_info.to_edge(UP+RIGHT)
        self.play(Write(text_info))
        
        self.wait(2)