import streamlit as st
import math
import os
import numpy as np
import matplotlib.pyplot as plt

# --- Windows環境向けの日本語フォント設定 ---
plt.rcParams['font.family'] = 'Meiryo'  # または 'MS Gothic', 'Yu Gothic' など

# --- サイドバーによる画面切り替え ---
st.sidebar.title("メニュー選択")
app_mode = st.sidebar.selectbox(
    "使用する計算・生成ツールを選んでください",
    [
        "梁のたわみ計算", 
        "エアシリンダ推力計算", 
        "吸着パッドの保持力計算",
        "波形グラフ生成（台形波・三角波）",
        "モータの必要トルク計算",
        "設計用 単位換算ツール",
        "巻回構造の径・断面グラフ計算"
    ]
)

# ==========================================
# 1. 梁のたわみ計算ツール
# ==========================================
if app_mode == "梁のたわみ計算":
    st.title("梁のたわみ計算ツール")

    material_database = {
        "一般構造用鋼 (SS400)": 205000.0,
        "アルミニウム合金 (A5052)": 70000.0,
        "ステンレス鋼 (SUS304)": 193000.0,
        "カスタム（手動入力）": 0.0
    }

    st.subheader("■ 条件設定と支持条件の選択")

    support_type = st.selectbox(
        "梁の支持条件と荷重形式",
        [
            "単純支持梁（中央集中荷重）",
            "両端固定梁（中央集中荷重）",
            "片持ち梁（先端集中荷重）"
        ]
    )

    if support_type == "単純支持梁（中央集中荷重）":
        if os.path.exists("simple_beam.png"):
            st.image("simple_beam.png", caption="単純支持梁（中央集中荷重）", width=350)
        st.markdown("両端が支持され、中央に集中荷重 $P$ が作用する梁の最大たわみ $\\delta$ の公式：")
        st.latex(r"\delta = \frac{P L^3}{48 E I}")
        deflection_coeff = 48.0

    elif support_type == "両端固定梁（中央集中荷重）":
        if os.path.exists("fixed_beam.png"):
            st.image("fixed_beam.png", caption="両端固定梁（中央集中荷重）", width=350)
        st.markdown("両端が完全に固定され、中央に集中荷重 $P$ が作用する梁の最大たわみ $\\delta$ の公式：")
        st.latex(r"\delta = \frac{P L^3}{192 E I}")
        deflection_coeff = 192.0

    else:
        if os.path.exists("cantilever_beam.png"):
            st.image("cantilever_beam.png", caption="片持ち梁（先端集中荷重）", width=350)
        st.markdown("一端が固定され、先端に集中荷重 $P$ が作用する梁の最大たわみ $\\delta$ の公式：")
        st.latex(r"\delta = \frac{P L^3}{3 E I}")
        deflection_coeff = 3.0

    st.info(
        "**【記号の意味】**\n"
        "- $\\delta$: 最大たわみ (mm)\n"
        "- $P$: 集中荷重 (N)\n"
        "- $L$: スパン長 (mm)\n"
        "- $E$: ヤング率 (MPa)\n"
        "- $I$: 断面二次モーメント (mm$^4$)"
    )

    selected_material = st.selectbox("材料の選択", list(material_database.keys()))

    if selected_material == "カスタム（手動入力）":
        young_modulus = st.number_input("ヤング率 E (MPa)", value=200000.0)
    else:
        default_e = material_database[selected_material]
        young_modulus = st.number_input("ヤング率 E (MPa)", value=default_e)

    load_n = st.number_input("集中荷重 P (N)", value=1000.0)
    span_mm = st.number_input("スパン長 L (mm)", value=1000.0)

    st.subheader("■ 断面形状と寸法の確認")
    section_type = st.selectbox(
        "断面の形", 
        ["長方形断面", "丸棒（中実円）", "パイプ（中空円管）", "H形鋼断面"]
    )

    if section_type == "長方形断面":
        st.markdown("---")
        st.markdown("##### 📐 長方形断面の公式と寸法")
        if os.path.exists("rect_beam.png"):
            st.image("rect_beam.png", caption="長方形断面の寸法図 (b: 幅, h: 高さ)", width=250)
        st.latex(r"I = \frac{b h^3}{12}")
        b = st.number_input("断面の幅 b (mm)", value=50.0)
        h = st.number_input("断面の高さ h (mm)", value=100.0)
        inertia_moment = (b * (h ** 3)) / 12.0

    elif section_type == "丸棒（中実円）":
        st.markdown("---")
        st.markdown("##### 📐 丸棒（中実円）の公式と寸法")
        if os.path.exists("circle_beam.png"):
            st.image("circle_beam.png", caption="丸棒の寸法図 (D: 直径)", width=250)
        st.latex(r"I = \frac{\pi D^4}{64}")
        D = st.number_input("直径 D (mm)", value=50.0)
        inertia_moment = (math.pi * (D ** 4)) / 64.0

    elif section_type == "パイプ（中空円管）":
        st.markdown("---")
        st.markdown("##### 📐 パイプ（中空円管）の公式と寸法")
        if os.path.exists("pipe_beam.png"):
            st.image("pipe_beam.png", caption="パイプの寸法図 (D: 外径, d: 内径)", width=250)
        st.latex(r"I = \frac{\pi (D^4 - d^4)}{64}")
        outer_d = st.number_input("外径 D (mm)", value=60.0)
        inner_d = st.number_input("内径 d (mm)", value=40.0)
        
        if inner_d >= outer_d:
            st.error("内径は外径より小さい値を設定してください。")
            inertia_moment = 0.0
        else:
            inertia_moment = (math.pi * ((outer_d ** 4) - (inner_d ** 4))) / 64.0

    else:
        st.markdown("---")
        st.markdown("##### 📐 H形鋼断面の公式と寸法")
        if os.path.exists("h_beam.png"):
            st.image("h_beam.png", caption="H形鋼の寸法図 (H, B, h, b)", width=300)
        st.latex(r"I = \frac{B H^3 - b h^3}{12}")
        H = st.number_input("全高 H (mm)", value=100.0)
        B = st.number_input("フランジ幅 B (mm)", value=100.0)
        h = st.number_input("ウェブ内高 h (mm)", value=80.0)
        b = st.number_input("ウェブ間隙 b (mm)", value=94.0)
        
        if h >= H or b >= B:
            st.error("内側の寸法（h, b）は外側の寸法（H, B）より小さく設定してください。")
            inertia_moment = 0.0
        else:
            inertia_moment = (B * (H ** 3) - b * (h ** 3)) / 12.0

    st.markdown("---")
    if st.button("計算する"):
        if inertia_moment <= 0:
            st.warning("正しい寸法を入力してください。")
        else:
            max_deflection = (load_n * (span_mm ** 3)) / (deflection_coeff * young_modulus * inertia_moment)
            st.success("計算完了！")
            st.write(f"■ 選択支持条件: **{support_type}**")
            st.write(f"■ 選択材料: **{selected_material}** (E = {young_modulus:,.1f} MPa)")
            st.write(f"■ 選択形状: **{section_type}**")
            st.write(f"■ 断面二次モーメント (I): {inertia_moment:,.1f} mm^4")
            st.metric(label="最大たわみ (δ)", value=f"{max_deflection:.4f} mm")


# ==========================================
# 2. エアシリンダ推力計算ツール
# ==========================================
elif app_mode == "エアシリンダ推力計算":
    st.title("エアシリンダ推力計算ツール")

    st.subheader("■ エアシリンダの条件設定と公式")
    st.markdown("エアシリンダの理論推力 $F$ の計算式：")
    st.latex(r"F = P \times A")
    st.info(
        "**【受圧面積 $A$ の求め方】**\n"
        "- **押し側 (Push)**: $A = \\frac{\\pi D^2}{4}$\n"
        "- **引き側 (Pull)**: $A = \\frac{\\pi (D^2 - d^2)}{4}$\n"
        "（※ $P$: 使用圧力 [MPa], $D$: チューブ内径 [mm], $d$: ロッド径 [mm]）"
    )

    action_type = st.selectbox("動作方向の選択", ["押し側 (Push)", "引き側 (Pull)"])
    bore_size = st.number_input("チューブ内径 D (mm)", value=50.0)

    if action_type == "引き側 (Pull)":
        rod_size = st.number_input("ロッド径 d (mm)", value=20.0)
    else:
        rod_size = 0.0

    pressure_mpa = st.number_input("使用圧力 P (MPa)", value=0.5)
    efficiency = st.slider("効率・負荷率（実用推力考慮）", min_value=0.5, max_value=1.0, value=0.8, step=0.05)

    st.markdown("---")
    if st.button("推力を計算する"):
        if bore_size <= 0 or pressure_mpa <= 0:
            st.warning("正しい数値を入力してください。")
        else:
            if action_type == "押し側 (Push)":
                area = (math.pi * (bore_size ** 2)) / 4.0
            else:
                if rod_size >= bore_size:
                    st.error("ロッド径はチューブ内径より小さく設定してください。")
                    area = 0.0
                else:
                    area = (math.pi * ((bore_size ** 2) - (rod_size ** 2))) / 4.0

            if area > 0:
                theoretical_thrust = pressure_mpa * area
                actual_thrust = theoretical_thrust * efficiency

                st.success("計算完了！")
                st.write(f"■ 動作方向: **{action_type}**")
                st.write(f"■ チューブ内径 (D): {bore_size} mm")
                if action_type == "引き側 (Pull)":
                    st.write(f"■ ロッド径 (d): {rod_size} mm")
                st.write(f"■ 使用圧力 (P): {pressure_mpa} MPa")
                st.write(f"■ 有効受圧面積 (A): {area:,.1f} mm$^2$")
                st.write(f"■ 理論推力: {theoretical_thrust:,.1f} N （約 {theoretical_thrust/9.80665:,.1f} kgf）")
                st.metric(label="実用推力（効率考慮）", value=f"{actual_thrust:,.1f} N （約 {actual_thrust/9.80665:,.1f} kgf）")


# ==========================================
# 3. 吸着パッドの保持力計算ツール
# ==========================================
elif app_mode == "吸着パッドの保持力計算":
    st.title("吸着パッドの保持力（吸着力）計算ツール")

    st.subheader("■ 吸着力の理論式と条件設定")
    st.markdown("真空パッドの理論吸着力 $W$ の計算式：")
    st.latex(r"W = \frac{\pi D^2}{4} \times P \times 0.001")
    st.info(
        "**【記号と条件の見方】**\n"
        "- $W$: 理論吸着力 (N)\n"
        "- $D$: パッド直径 (mm)\n"
        "- $P$: 真空度 (kPa)\n"
        "- **安全率の目安**: 水平吊り時は **4 以上**、垂直吊り時は **8 以上** を考慮します。"
    )

    pad_diameter = st.number_input("パッド直径 D (mm)", value=40.0)
    vacuum_deg = st.number_input("真空度 P (kPa)", value=60.0)
    
    lifting_direction = st.selectbox(
        "ワークの搬送・保持状態",
        ["水平吊り（安全率 4 考慮）", "垂直吊り（安全率 8 考慮）", "カスタム安全率"]
    )

    if lifting_direction == "水平吊り（安全率 4 考慮）":
        safety_factor = 4.0
    elif lifting_direction == "垂直吊り（安全率 8 考慮）":
        safety_factor = 8.0
    else:
        safety_factor = st.number_input("カスタム安全率", value=4.0, min_value=1.0)

    st.markdown("---")
    if st.button("保持力を計算する"):
        if pad_diameter <= 0 or vacuum_deg <= 0:
            st.warning("正しい数値を入力してください。")
        else:
            area = (math.pi * (pad_diameter ** 2)) / 4.0
            theoretical_force = area * vacuum_deg * 0.001
            allowable_force = theoretical_force / safety_factor

            st.success("計算完了！")
            st.write(f"■ パッド直径 (D): {pad_diameter} mm")
            st.write(f"■ 真空度 (P): {vacuum_deg} kPa")
            st.write(f"■ パッド受圧面積 (A): {area:,.1f} mm$^2$")
            st.write(f"■ 理論吸着力: {theoretical_force:,.1f} N （約 {theoretical_force/9.80665:,.2f} kgf）")
            st.metric(
                label="実用保持力（安全率考慮）", 
                value=f"{allowable_force:,.1f} N （約 {allowable_force/9.80665:,.2f} kgf）"
            )


# ==========================================
# 4. 波形グラフ生成（台形波・三角波）
# ==========================================
elif app_mode == "波形グラフ生成（台形波・三角波）":
    st.title("波形グラフ生成ツール（台形波・三角波）")

    st.subheader("■ 入力モードの選択")
    calc_mode = st.selectbox(
        "設計条件の入力方法を選択してください",
        [
            "ストローク ＋ 最高速度 ＋ 加速度",
            "ストローク ＋ 最高速度 ＋ タクト（総時間）",
            "ストローク ＋ 加速度 ＋ タクト（総時間）"
        ]
    )

    st.markdown("---")
    stroke = st.number_input("総移動距離 (Stroke, mm)", value=100.0)

    v_max = 0.0
    accel = 0.0
    tact_time = 0.0

    if calc_mode == "ストローク ＋ 最高速度 ＋ 加速度":
        v_max = st.number_input("目標最高速度 (Max Velocity, mm/s)", value=500.0)
        accel = st.number_input("加速度・減速度 (Acceleration, mm/s^2)", value=2500.0)
    elif calc_mode == "ストローク ＋ 最高速度 ＋ タクト（総時間）":
        v_max = st.number_input("目標最高速度 (Max Velocity, mm/s)", value=500.0)
        tact_time = st.number_input("目標タクトタイム (Total Time, s)", value=0.5)
    else:
        accel = st.number_input("加速度・減速度 (Acceleration, mm/s^2)", value=2500.0)
        tact_time = st.number_input("目標タクトタイム (Total Time, s)", value=0.5)

    st.markdown("---")
    if st.button("波形を判定・描画する"):
        if stroke <= 0:
            st.warning("ストロークには正の数値を入力してください。")
        else:
            is_valid = True
            wave_shape = ""
            t_total = 0.0
            t_plot = np.array([])
            v_plot = np.array([])
            calculated_info = ""

            if calc_mode == "ストローク ＋ 最高速度 ＋ 加速度":
                if v_max <= 0 or accel <= 0:
                    st.warning("最高速度と加速度には正の数値を入力してください。")
                    is_valid = False
                else:
                    l_acc = (v_max ** 2) / accel
                    if stroke >= l_acc:
                        wave_shape = "台形波 (Trapezoidal Wave)"
                        t_acc = v_max / accel
                        t_const = (stroke - l_acc) / v_max
                        t_total = (2 * t_acc) + t_const
                        t_plot = np.array([0, t_acc, t_acc + t_const, t_total])
                        v_plot = np.array([0, v_max, v_max, 0])
                        calculated_info = f"- 加減速時間: {t_acc:.3f} s\n- 一定速走行時間: {t_const:.3f} s\n- 総所要時間 (タクト): {t_total:.3f} s"
                    else:
                        wave_shape = "三角波 (Triangular Wave)"
                        t_acc = math.sqrt(stroke / accel)
                        t_total = 2 * t_acc
                        v_peak = accel * t_acc
                        t_plot = np.array([0, t_acc, t_total])
                        v_plot = np.array([0, v_peak, 0])
                        calculated_info = f"- 到達ピーク速度: {v_peak:.1f} mm/s (設定最高速度未満)\n- 総所要時間 (タクト): {t_total:.3f} s"

            elif calc_mode == "ストローク ＋ 最高速度 ＋ タクト（総時間）":
                if v_max <= 0 or tact_time <= 0:
                    st.warning("最高速度とタクトタイムには正の数値を入力してください。")
                    is_valid = False
                else:
                    if v_max * tact_time >= 2 * stroke:
                        wave_shape = "台形波 (Trapezoidal Wave)"
                        t_acc = tact_time - (stroke / v_max)
                        if t_acc <= 0:
                            st.error("指定された最高速度とタクトでは時間を満たせません。")
                            is_valid = False
                        else:
                            accel = (v_max ** 2) / (v_max * tact_time - stroke)
                            t_const = tact_time - (2 * t_acc)
                            t_total = tact_time
                            t_plot = np.array([0, t_acc, t_acc + t_const, t_total])
                            v_plot = np.array([0, v_max, v_max, 0])
                            calculated_info = f"- 逆算された加速度: {accel:,.1f} mm/s^2\n- 加減速時間: {t_acc:.3f} s\n- 一定速走行時間: {t_const:.3f} s\n- 総所要時間: {t_total:.3f} s"
                    else:
                        st.error("指定されたストロークに対して最高速度が低すぎるか、タクトが短すぎます。")
                        is_valid = False

            else:
                if accel <= 0 or tact_time <= 0:
                    st.warning("加速度とタクトタイムには正の数値を入力してください。")
                    is_valid = False
                else:
                    discriminant = (accel * (tact_time ** 2)) - (4 * stroke)
                    if discriminant >= 0:
                        wave_shape = "台形波 (または三角波の限界)"
                        v_max = (accel * tact_time - math.sqrt(discriminant)) / 2.0
                        t_acc = v_max / accel
                        t_const = tact_time - (2 * t_acc)
                        t_total = tact_time
                        if t_const < 0:
                            t_const = 0.0
                            wave_shape = "三角波 (Triangular Wave)"
                        t_plot = np.array([0, t_acc, t_acc + t_const, t_total])
                        v_plot = np.array([0, v_max, v_max, 0])
                        calculated_info = f"- 逆算された最高(ピーク)速度: {v_max:,.1f} mm/s\n- 加減速時間: {t_acc:.3f} s\n- 一定速走行時間: {t_const:.3f} s\n- 総所要時間: {t_total:.3f} s"
                    else:
                        st.error("指定された加速度とタクトでは、そのストロークに到達できません。")
                        is_valid = False

            if is_valid:
                st.success(f"判定結果： **{wave_shape}**")
                st.info(calculated_info)

                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(t_plot, v_plot, color='#2563eb', linewidth=2.5, marker='o')
                ax.set_title(f"Motor Velocity Profile: {wave_shape}", fontsize=14, fontweight='bold')
                ax.set_xlabel("Time (s)", fontsize=12)
                ax.set_ylabel("Velocity (mm/s)", fontsize=12)
                ax.grid(True, linestyle='--', alpha=0.6)
                ax.set_ylim(0, max(v_plot) * 1.3 if max(v_plot) > 0 else 10)

                st.pyplot(fig)


# ==========================================
# 5. モータの必要トルク計算ツール
# ==========================================
elif app_mode == "モータの必要トルク計算":
    st.title("モータの必要トルク計算ツール（減速比・慣性分離対応）")

    st.subheader("■ 計算公式と条件設定")
    st.markdown("減速比 $N$ （モータ回転数 / ネジ軸回転数）を考慮したモータ軸換算の必要トルク $T$ の計算式：")
    st.latex(r"T = \left( \frac{T_L}{N \cdot \eta} + (J_m + \frac{J_l}{N^2}) \cdot \alpha_m \right) \times S")
    st.info(
        "**【記号と条件の見方】**\n"
        "- $N$: 減速比（モータ側回転数 / ボールねじ側回転数。直結の場合は 1）\n"
        "- $T_L$: ボールネジ軸換算の負荷トルク (N·m) $\\rightarrow T_L = \\frac{F \\cdot l}{2000 \\cdot \\pi}$\n"
        "- $J_m$: モータ軸の慣性モーメント (kg·m$^2$)\n"
        "- $J_l$: 負荷側（ボールネジ・ワーク）の慣性モーメント (kg·m$^2$)\n"
        "- $\\alpha_m$: モータ軸の角加速度 (rad/s$^2$) $\\rightarrow \\alpha_m = \\alpha_{screw} \\times N$\n"
        "- $\\eta$: 機械効率 (-)\n"
        "- $S$: 安全率"
    )

    st.subheader("■ 条件入力")
    col1, col2 = st.columns(2)
    with col1:
        gear_ratio = st.number_input("減速比 N (モータ:ネジ)", value=1.0, min_value=0.01, step=0.1)
        work_mass = st.number_input("ワーク・可動部質量 W (kg)", value=10.0)
        lead_mm = st.number_input("ボールネジリード l (mm)", value=10.0)
        efficiency = st.number_input("機械効率 η", value=0.9, min_value=0.1, max_value=1.0, step=0.05)
    with col2:
        friction_mu = st.number_input("摩擦係数 μ", value=0.1, min_value=0.0, max_value=1.0, step=0.01)
        v_max = st.number_input("最高速度 V (mm/s)", value=500.0)
        accel_time = st.number_input("加速時間 t_a (s)", value=0.2)
        motor_inertia = st.number_input("モータ軸 慣性モーメント J_m (kg·m^2)", value=0.0001)
        safety_factor = st.slider("安全率 S", min_value=1.0, max_value=2.0, value=1.5, step=0.1)

    st.markdown("---")
    if st.button("必要トルクを計算する"):
        if work_mass <= 0 or lead_mm <= 0 or accel_time <= 0 or v_max <= 0 or gear_ratio <= 0:
            st.warning("正しい数値を入力してください。")
        else:
            force_f = friction_mu * work_mass * 9.80665
            torque_l_screw = (force_f * lead_mm) / (2000.0 * math.pi)
            torque_l_motor = torque_l_screw / (gear_ratio * efficiency)
            inertia_l = work_mass * ((lead_mm / (2000.0 * math.pi)) ** 2)
            inertia_l_motor = inertia_l / (gear_ratio ** 2)
            angular_accel_screw = (2.0 * math.pi * v_max) / (lead_mm * accel_time)
            angular_accel_motor = angular_accel_screw * gear_ratio
            total_inertia_motor = motor_inertia + inertia_l_motor
            torque_a = total_inertia_motor * angular_accel_motor
            required_torque = (torque_l_motor + torque_a) * safety_factor

            screw_rpm = (v_max * 60.0) / lead_mm
            motor_rpm = screw_rpm * gear_ratio

            st.success("計算完了！")
            st.write(f"■ 減速比 (N): {gear_ratio} : 1")
            st.write(f"■ ボールねじ軸 回転速度: **{screw_rpm:,.1f} rpm**")
            st.write(f"■ モータ軸 回転速度: **{motor_rpm:,.1f} rpm**")
            st.write(f"■ 摩擦力 (F): {force_f:.2f} N")
            st.write(f"■ モータ軸換算 負荷トルク ($T_{{L\_motor}}$): {torque_l_motor:.4f} N·m")
            st.write(f"■ 負荷側慣性モーメント ($J_l$): {inertia_l:.6f} kg·m$^2$")
            st.write(f"■ モータ軸換算 負荷慣性モーメント ($J_l / N^2$): {inertia_l_motor:.6f} kg·m$^2$")
            st.write(f"■ モータ軸 合計慣性モーメント ($J_m + J_l/N^2$): {total_inertia_motor:.6f} kg·m$^2$")
            st.write(f"■ 加速トルク ($T_a$): {torque_a:.4f} N·m")
            st.metric(
                label=f"モータ軸 必要ピークトルク（安全率 {safety_factor} 考慮）",
                value=f"{required_torque:.3f} N·m （約 {required_torque * 10.197:,.1f} kgf·cm）"
            )


# ==========================================
# 6. 設計用 単位換算ツール
# ==========================================
elif app_mode == "設計用 単位換算ツール":
    st.title("設計実務用 単位換算ツール")
    st.markdown("機械・設備設計の現場で日常的に使用する主要な単位換算の式と、即座に計算できる変換セルです。")

    conv_tab1, conv_tab2, conv_tab3, conv_tab4, conv_tab5 = st.tabs([
        "① 力・荷重", 
        "② 圧力", 
        "③ トルク", 
        "④ 速度・回転数", 
        "⑤ 慣性モーメント"
    ])

    with conv_tab1:
        st.subheader("■ 力・荷重の換算式")
        st.markdown(
            "- $1 \\text{ kgf} = 9.80665 \\text{ N}$\n"
            "- $1 \\text{ N} \\approx 0.10197 \\text{ kgf}$\n"
            "- $1 \\text{ kN} = 1000 \\text{ N} \\approx 101.97 \\text{ kgf}$"
        )
        st.markdown("---")
        st.subheader("■ 変換セル")
        force_val = st.number_input("入力値", value=100.0, key="force_input")
        force_unit = st.selectbox("入力単位", ["ニュートン (N)", "キログラム重 (kgf)", "キロニュートン (kN)"])
        
        if force_unit == "ニュートン (N)":
            val_n = force_val
        elif force_unit == "キログラム重 (kgf)":
            val_n = force_val * 9.80665
        else:
            val_n = force_val * 1000.0

        col_f1, col_f2, col_f3 = st.columns(3)
        col_f1.metric("N (ニュートン)", f"{val_n:,.2f} N")
        col_f2.metric("kgf (キログラム重)", f"{val_n / 9.80665:,.2f} kgf")
        col_f3.metric("kN (キロニュートン)", f"{val_n / 1000.0:,.4f} kN")

    with conv_tab2:
        st.subheader("■ 圧力の換算式")
        st.markdown(
            "- $1 \\text{ MPa} = 1000 \\text{ kPa} = 10 \\text{ bar} \\approx 10.197 \\text{ kgf/cm}^2$\n"
            "- $1 \\text{ bar} = 100 \\text{ kPa} = 0.1 \\text{ MPa} \\approx 1.0197 \\text{ kgf/cm}^2$\n"
            "- $1 \\text{ kgf/cm}^2 \\approx 0.0980665 \\text{ MPa} = 98.0665 \\text{ kPa}$"
        )
        st.markdown("---")
        st.subheader("■ 変換セル")
        p_val = st.number_input("入力値", value=0.5, key="pressure_input")
        p_unit = st.selectbox("入力単位", ["メガパスカル (MPa)", "キロパスカル (kPa)", "バール (bar)", "kgf/cm²"])

        if p_unit == "メガパスカル (MPa)":
            val_mpa = p_val
        elif p_unit == "キロパスカル (kPa)":
            val_mpa = p_val / 1000.0
        elif p_unit == "バール (bar)":
            val_mpa = p_val * 0.1
        else:
            val_mpa = p_val * 0.0980665

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        col_p1.metric("MPa", f"{val_mpa:.4f} MPa")
        col_p2.metric("kPa", f"{val_mpa * 1000:,.1f} kPa")
        col_p3.metric("bar", f"{val_mpa * 10:.3f} bar")
        col_p4.metric("kgf/cm²", f"{val_mpa / 0.0980665:.3f} kgf/cm²")

    with conv_tab3:
        st.subheader("■ トルクの換算式")
        st.markdown(
            "- $1 \\text{ N}\\cdot\\text{m} = 100 \\text{ N}\\cdot\\text{cm} \\approx 10.197 \\text{ kgf}\\cdot\\text{cm} \\approx 0.10197 \\text{ kgf}\\cdot\\text{m}$\n"
            "- $1 \\text{ kgf}\\cdot\\text{cm} \\approx 0.0980665 \\text{ N}\\cdot\\text{m} = 9.80665 \\text{ N}\\cdot\\text{cm}$"
        )
        st.markdown("---")
        st.subheader("■ 変換セル")
        t_val = st.number_input("入力値", value=1.0, key="torque_input")
        t_unit = st.selectbox("入力単位", ["N·m (ニュートンメートル)", "N·cm (ニュートンセンチ)", "kgf·cm", "kgf·m"])

        if t_unit == "N·m (ニュートンメートル)":
            val_nm = t_val
        elif t_unit == "N·cm (ニュートンセンチ)":
            val_nm = t_val / 100.0
        elif t_unit == "kgf·cm":
            val_nm = t_val * 0.0980665
        else:
            val_nm = t_val * 9.80665

        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        col_t1.metric("N·m", f"{val_nm:.4f} N·m")
        col_t2.metric("N·cm", f"{val_nm * 100:.2f} N·cm")
        col_t3.metric("kgf·cm", f"{val_nm / 0.0980665:.2f} kgf·cm")
        col_t4.metric("kgf·m", f"{val_nm / 9.80665:.4f} kgf·m")

    with conv_tab4:
        st.subheader("■ 直線速度 ↔ 回転速度 (rpm) の設計換算式")
        st.latex(r"N_{rpm} = \frac{V \times 60}{l}")
        st.markdown(
            "- $1 \\text{ m/s} = 1000 \\text{ mm/s} = 60 \\text{ m/min} = 3.6 \\text{ km/h}$\n"
            "- **ボールねじ回転数換算**: リード $l$ (mm/rev) と直線速度 $V$ (mm/s) より $N = (V \\times 60) / l$"
        )
        st.markdown("---")
        st.subheader("■ 送り速度 ↔ 回転数 相互計算セル")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            speed_mms = st.number_input("直線移動速度 V (mm/s)", value=500.0)
            screw_lead = st.number_input("ボールねじリード l (mm)", value=10.0, key="lead_conv")
            calculated_rpm = (speed_mms * 60.0) / screw_lead
            st.metric("換算回転数 (rpm)", f"{calculated_rpm:,.1f} rpm")
        with col_v2:
            st.metric("分速換算 (m/min)", f"{(speed_mms * 60.0) / 1000.0:.2f} m/min")
            st.metric("時速換算 (km/h)", f"{(speed_mms * 3.6) / 1000.0:.2f} km/h")

    with conv_tab5:
        st.subheader("■ 慣性モーメント (J) の換算式")
        st.markdown(
            "- $1 \\text{ kg}\\cdot\\text{m}^2 = 10^4 \\text{ kg}\\cdot\\text{cm}^2 = 10^7 \\text{ g}\\cdot\\text{cm}^2 \\approx 10.197 \\text{ kgf}\\cdot\\text{cm}\\cdot\\text{s}^2$\n"
            "- $1 \\text{ kgf}\\cdot\\text{cm}\\cdot\\text{s}^2 \\approx 0.0980665 \\text{ kg}\\cdot\\text{m}^2 = 980.665 \\text{ kg}\\cdot\\text{cm}^2$"
        )
        st.markdown("---")
        st.subheader("■ 変換セル")
        j_val = st.number_input("入力値", value=0.0010, format="%.6f", key="inertia_input")
        j_unit = st.selectbox("入力単位", ["kg·m²", "kg·cm²", "g·cm²", "kgf·cm·s²"])

        if j_unit == "kg·m²":
            val_kgm2 = j_val
        elif j_unit == "kg·cm²":
            val_kgm2 = j_val * 1e-4
        elif j_unit == "g·cm²":
            val_kgm2 = j_val * 1e-7
        else:
            val_kgm2 = j_val * 0.0980665

        col_j1, col_j2, col_j3, col_j4 = st.columns(4)
        col_j1.metric("kg·m²", f"{val_kgm2:.6f}")
        col_j2.metric("kg·cm²", f"{val_kgm2 * 1e4:,.2f}")
        col_j3.metric("g·cm²", f"{val_kgm2 * 1e7:,.0f}")
        col_j4.metric("kgf·cm·s²", f"{val_kgm2 / 0.0980665:.6f}")


# ==========================================
# 7. 巻回構造の径・断面グラフ計算（導出式解説付き）
# ==========================================
elif app_mode == "巻回構造の径・断面グラフ計算":
    st.title("巻回構造の径・断面グラフ計算ツール")

    st.subheader("■ 巻回構造の計算モデルと導出過程の式")
    st.markdown(
        "中心の巻き軸（真円または楕円）に、**電解紙 → ＋箔 → 電解紙 → －箔** の順で材料を連続して巻き付ける構造は、"
        "数学的に**「アルキメデスの螺旋（スパイラル）」**として表されます。"
    )
    
    st.markdown("##### 1. 1ターン（1周）あたりの総厚み ($T$) の算出")
    st.markdown("各層の厚みを足し合わせることで、1周進むごとに半径がどれだけ増えるかが決まります。")
    st.latex(r"T = t_{\text{paper1}} + t_{\text{pos}} + t_{\text{paper2}} + t_{\text{neg}}")

    st.markdown("##### 2. 角度 $\theta$ における半径・座標の導出（螺旋方程式）")
    st.markdown("中心からの回転角度を $\\theta$ （ラジアン）とするとき、巻き進みに伴う半径の変化は次式で表されます。")
    st.latex(r"R(\theta) = R_0 + \frac{T}{2\pi} \theta \quad (\text{真円の場合})")
    st.latex(r"a(\theta) = a_0 + \frac{T}{2\pi} \theta, \quad b(\theta) = b_0 + \frac{T}{2\pi} \theta \quad (\text{楕円の場合})")
    st.markdown(
        "これを直交座標 $(x, y)$ に変換し、各層の厚みオフセットを加えながら連続的な帯（バンド）として塗りつぶすことで、"
        "途切れない螺旋状の断面図を描画しています。"
    )

    st.markdown("---")
    st.subheader("■ 条件設定")
    shape_type = st.selectbox("巻き軸の形状", ["真円", "楕円"])

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if shape_type == "真円":
            d_core = st.number_input("巻き軸直径 D0 (mm)", value=10.0)
            a_core, b_core = d_core / 2.0, d_core / 2.0
        else:
            a_core = st.number_input("長軸 a0 (mm)", value=15.0) / 2.0
            b_core = st.number_input("短軸 b0 (mm)", value=10.0) / 2.0
            
    with col_s2:
        turns = st.number_input("ターン数 (回)", value=5, min_value=1, max_value=30, step=1)

    st.subheader("■ 材料厚み設定")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        t_pos = st.number_input("＋箔厚み (mm)", value=0.02, format="%.3f")
    with col_t2:
        t_paper = st.number_input("電解紙厚み (mm)", value=0.03, format="%.3f")
    with col_t3:
        t_neg = st.number_input("ー箔厚み (mm)", value=0.02, format="%.3f")

    st.markdown("---")
    if st.button("径を計算して螺旋断面を描画する"):
        layers = [
            ("電解紙 (1層目)", t_paper, "#fde047"), 
            ("＋箔", t_pos, "#ef4444"),           
            ("電解紙 (2層目)", t_paper, "#fef08a"), 
            ("ー箔", t_neg, "#3b82f6")            
        ]
        
        t_turn = sum([l[1] for l in layers])
        
        if shape_type == "真円":
            final_diameter = (a_core * 2.0) + (2.0 * turns * t_turn)
            st.success(f"計算完了！ 最終外径（{turns}ターン後）: **{final_diameter:.3f} mm**")
        else:
            final_a = (a_core * 2.0) + (2.0 * turns * t_turn)
            final_b = (b_core * 2.0) + (2.0 * turns * t_turn)
            st.success(f"計算完了！ 最終外形（{turns}ターン後）: 長軸 **{final_a:.3f} mm** / 短軸 **{final_b:.3f} mm**")

        # グラフ描画（連続螺旋構造）
        fig, ax = plt.subplots(figsize=(6, 6))
        
        theta_core = np.linspace(0, 2 * np.pi, 300)
        x_core = a_core * np.cos(theta_core)
        y_core = b_core * np.sin(theta_core)
        ax.fill(x_core, y_core, color='#94a3b8', label='巻き軸 (Core)')

        current_thickness_sum = 0.0
        
        for layer_name, t_thick, color in layers:
            theta_list = np.linspace(0, 2 * np.pi * turns, 1000 * turns)
            
            r_in_a = a_core + (current_thickness_sum) + (t_turn / (2 * np.pi)) * theta_list
            r_in_b = b_core + (current_thickness_sum) + (t_turn / (2 * np.pi)) * theta_list
            r_out_a = a_core + (current_thickness_sum + t_thick) + (t_turn / (2 * np.pi)) * theta_list
            r_out_b = b_core + (current_thickness_sum + t_thick) + (t_turn / (2 * np.pi)) * theta_list
            
            x_in = r_in_a * np.cos(theta_list)
            y_in = r_in_b * np.sin(theta_list)
            x_out = r_out_a * np.cos(theta_list)
            y_out = r_out_b * np.sin(theta_list)
            
            x_band = np.concatenate([x_in, x_out[::-1]])
            y_band = np.concatenate([y_in, y_out[::-1]])
            
            ax.fill(x_band, y_band, color=color, alpha=0.85, edgecolor='none', label=layer_name)
            current_thickness_sum += t_thick

        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_title(f"巻回構造の連続螺旋断面図 ({shape_type}軸 / {turns}ターン)", fontsize=14, fontweight='bold')
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.0))
        
        st.pyplot(fig)