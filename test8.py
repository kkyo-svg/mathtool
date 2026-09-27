import streamlit as st
import math
import os
import numpy as np
import matplotlib.pyplot as plt

# --- アプリの基本設定 ---
st.set_page_config(page_title="プロフェッショナル設計ポータル", layout="wide")

# --- セッションステートの初期化（単語帳の動的追加用） ---
if "dictionary_data" not in st.session_state:
    st.session_state.dictionary_data = {
        "電気・電子": {
            "コンデンサ": "電気を一時的に蓄えたり放出したりする受動部品。平滑化やノイズ除去に用いられる。",
            "アルミ電解コンデンサ": "電解液をしみこませた紙とアルミ箔を巻いた構造の大容量コンデンサ。"
        },
        "機械要素": {
            "ボールねじ": "回転運動を直線運動に高効率で変換する機械要素。",
            "断面二次モーメント": "梁の曲げに対する変形しにくさを表す幾何学量。"
        },
        "材料力学": {
            "ヤング率": "応力とひずみの比例関係を表す縦弾性係数。"
        }
    }

# --- サイドバーによる大カテゴリの切り替え（常に一覧表示されるラジオボタン） ---
st.sidebar.title("プロフェッショナル設計ツール")
main_category = st.sidebar.radio(
    "大カテゴリを選択してください",
    [
        "設計計算", 
        "関数・グラフ生成", 
        "電卓",
        "単語帳"
    ]
)

# ==========================================
# 1. 設計計算 カテゴリ（従来のツールをすべて網羅）
# ==========================================
if main_category == "設計計算":
    st.title("設計計算ツール群")
    
    # 従来の個別ツールをサブメニュー（ラジオボタン）として配置
    app_mode = st.radio(
        "実行する設計計算ツールを選んでください",
        [
            "梁のたわみ計算", 
            "エアシリンダ推力計算", 
            "吸着パッドの保持力計算",
            "波形グラフ生成（台形波・三角波）",
            "モータの必要トルク計算",
            "設計用 単位換算ツール",
            "巻回構造の径・断面グラフ計算"
        ],
        horizontal=True
    )
    st.markdown("---")

    # 1-1. 梁のたわみ計算
    if app_mode == "梁のたわみ計算":
        st.subheader("梁のたわみ計算ツール")

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

    # 1-2. エアシリンダ推力計算
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

    # 1-3. 吸着パッドの保持力計算
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

    # 1-4. 波形グラフ生成（台形波・三角波）
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

    # 1-5. モータの必要トルク計算
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

    # 1-6. 設計用 単位換算ツール
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

    # 1-7. 巻回構造の径・断面グラフ計算
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
                ("Paper (Layer 1)", t_paper, "#fde047"), 
                ("+ Foil", t_pos, "#ef4444"),           
                ("Paper (Layer 2)", t_paper, "#fef08a"), 
                ("- Foil", t_neg, "#3b82f6")            
            ]
            
            t_turn = sum([l[1] for l in layers])
            
            if shape_type == "真円":
                final_diameter = (a_core * 2.0) + (2.0 * turns * t_turn)
                st.success(f"計算完了！ 最終外径（{turns}ターン後）: **{final_diameter:.3f} mm**")
            else:
                final_a = (a_core * 2.0) + (2.0 * turns * t_turn)
                final_b = (b_core * 2.0) + (2.0 * turns * t_turn)
                st.success(f"計算完了！ 最終外形（{turns}ターン後）: 長軸 **{final_a:.3f} mm** / 短軸 **{final_b:.3f} mm**")

            fig, ax = plt.subplots(figsize=(6, 6))
            
            theta_core = np.linspace(0, 2 * np.pi, 300)
            x_core = a_core * np.cos(theta_core)
            y_core = b_core * np.sin(theta_core)
            ax.fill(x_core, y_core, color='#94a3b8', label='Core')

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
            ax.set_title(f"Winding Cross-Section ({shape_type} / {turns} Turns)", fontsize=12, fontweight='bold')
            ax.set_xlabel("X (mm)")
            ax.set_ylabel("Y (mm)")
            ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.0))
            
            st.pyplot(fig)


# ==========================================
# 2. 関数・グラフ生成 カテゴリ
# ==========================================
elif main_category == "関数・グラフ生成":
    st.title("関数・グラフ生成ツール")
    st.markdown("スマホで簡単に数式を入力できるよう、主要な文字・記号の入力ボタンを設置しています。")

    # 1. 最初に確実にセッションステートを初期化する
    if "func_expr" not in st.session_state:
        st.session_state.func_expr = "x**2 - 4"

    # 2. st.text_input には key="func_expr" のみを指定し、左辺への代入はしない
    st.text_input("関数を入力してください (変数: x)", key="func_expr")

    # スマホ用入力補助キーパッド
    with st.expander("📱 スマホ用 入力補助キーパッドを開く", expanded=False):
        st.caption("ボタンをタップすると入力欄に文字が追加されます。")
        col_b1, col_b2, col_b3, col_b4, col_b5, col_b6 = st.columns(6)
        if col_b1.button("x", key="fn_x"): st.session_state.func_expr += "x"; st.rerun()
        if col_b2.button("+", key="fn_add"): st.session_state.func_expr += "+"; st.rerun()
        if col_b3.button("-", key="fn_sub"): st.session_state.func_expr += "-"; st.rerun()
        if col_b4.button("×", key="fn_mul"): st.session_state.func_expr += "*"; st.rerun()
        if col_b5.button("÷", key="fn_div"): st.session_state.func_expr += "/"; st.rerun()
        if col_b6.button("^", key="fn_pow"): st.session_state.func_expr += "**"; st.rerun()

        col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
        if col_c1.button("sin(", key="fn_sin"): st.session_state.func_expr += "np.sin("; st.rerun()
        if col_c2.button("cos(", key="fn_cos"): st.session_state.func_expr += "np.cos("; st.rerun()
        if col_c3.button("log(", key="fn_log"): st.session_state.func_expr += "np.log("; st.rerun()
        if col_c4.button("sqrt(", key="fn_sqrt"): st.session_state.func_expr += "np.sqrt("; st.rerun()
        if col_c5.button("pi", key="fn_pi"): st.session_state.func_expr += "np.pi"; st.rerun()

        col_d1, col_d2, col_d3 = st.columns(3)
        if col_d1.button("(", key="fn_lp"): st.session_state.func_expr += "("; st.rerun()
        if col_d2.button(")", key="fn_rp"): st.session_state.func_expr += ")"; st.rerun()
        if col_d3.button("クリア", key="fn_clr"): st.session_state.func_expr = ""; st.rerun()

    col_x1, col_x2 = st.columns(2)
    with col_x1:
        x_min = st.number_input("X軸 最小値", value=-5.0)
    with col_x2:
        x_max = st.number_input("X軸 最大値", value=5.0)

    if st.button("グラフを描画する", key="fn_plot"):
        try:
            x = np.linspace(x_min, x_max, 400)
            allowed_names = {"x": x, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "pi": np.pi, "e": np.e}
            y = eval(st.session_state.func_expr, {"__builtins__": __builtins__}, allowed_names)

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(x, y, color='#2563eb', linewidth=2.5)
            ax.axhline(0, color='black', linewidth=1, linestyle='--')
            ax.axvline(0, color='black', linewidth=1, linestyle='--')
            ax.set_title(f"Graph of y = {st.session_state.func_expr}", fontsize=12, fontweight='bold')
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(True, linestyle='--', alpha=0.6)

            st.success("グラフの描画に成功しました！")
            st.pyplot(fig)

            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.metric("最大値 (Max y)", f"{np.max(y):.3f}")
            col_res2.metric("最小値 (Min y)", f"{np.min(y):.3f}")
            col_res3.metric("終点での値", f"{y[-1]:.3f}")

        except Exception as e:
            st.error(f"数式の評価中にエラーが発生しました: {e}")


# ==========================================
# 3. 電卓 カテゴリ（ボタン式関数電卓）
# ==========================================
elif main_category == "電卓":
    st.title("関数電卓・単位換算・集計ツール")
    calc_tab1, calc_tab2, calc_tab3 = st.tabs(["関数電卓", "単位換算ツール", "データ集計・統計"])

    with calc_tab1:
        st.subheader("ボタン式関数電卓")
        st.markdown("画面上のボタンをタップして数式を組み立て、計算を実行できます。")

        # 入力式を保持するセッションステートの初期化
        if "calc_expr" not in st.session_state:
            st.session_state.calc_expr = ""

        # 現在の入力式を表示するディスプレイ部分
        current_display = st.session_state.calc_expr if st.session_state.calc_expr else "0"
        st.info(f"**入力式:** {current_display}")

        # --- 電卓キーパッドの配置 ---
        # 1行目: クリア、カッコ、割り算
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("C", key="calc_c"): 
            st.session_state.calc_expr = ""
            st.rerun()
        if c2.button("(", key="calc_lp"): 
            st.session_state.calc_expr += "("
            st.rerun()
        if c3.button(")", key="calc_rp"): 
            st.session_state.calc_expr += ")"
            st.rerun()
        if c4.button("÷", key="calc_div"): 
            st.session_state.calc_expr += "/"
            st.rerun()

        # 2行目: 7, 8, 9, ×
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("7", key="calc_7"): 
            st.session_state.calc_expr += "7"
            st.rerun()
        if c2.button("8", key="calc_8"): 
            st.session_state.calc_expr += "8"
            st.rerun()
        if c3.button("9", key="calc_9"): 
            st.session_state.calc_expr += "9"
            st.rerun()
        if c4.button("×", key="calc_mul"): 
            st.session_state.calc_expr += "*"
            st.rerun()

        # 3行目: 4, 5, 6, -
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("4", key="calc_4"): 
            st.session_state.calc_expr += "4"
            st.rerun()
        if c2.button("5", key="calc_5"): 
            st.session_state.calc_expr += "5"
            st.rerun()
        if c3.button("6", key="calc_6"): 
            st.session_state.calc_expr += "6"
            st.rerun()
        if c4.button("-", key="calc_sub"): 
            st.session_state.calc_expr += "-"
            st.rerun()

        # 4行目: 1, 2, 3, +
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("1", key="calc_1"): 
            st.session_state.calc_expr += "1"
            st.rerun()
        if c2.button("2", key="calc_2"): 
            st.session_state.calc_expr += "2"
            st.rerun()
        if c3.button("3", key="calc_3"): 
            st.session_state.calc_expr += "3"
            st.rerun()
        if c4.button("+", key="calc_add"): 
            st.session_state.calc_expr += "+"
            st.rerun()

        # 5行目: 0, ., 1文字削除(⌫), ＝
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("0", key="calc_0"): 
            st.session_state.calc_expr += "0"
            st.rerun()
        if c2.button(".", key="calc_dot"): 
            st.session_state.calc_expr += "."
            st.rerun()
        if c3.button("⌫", key="calc_bs"): 
            st.session_state.calc_expr = st.session_state.calc_expr[:-1]
            st.rerun()
        if c4.button("＝", key="calc_eq"):
            try:
                calc_scope = {
                    "sin": math.sin, "cos": math.cos, "tan": math.tan, 
                    "sqrt": math.sqrt, "pi": math.pi, "e": math.e, 
                    "radians": math.radians, "log": math.log
                }
                result = eval(st.session_state.calc_expr, {"__builtins__": {}}, calc_scope)
                st.success(f"計算結果: **{result}**")
            except Exception as e:
                st.error(f"計算エラー: {e}")

        # 6行目: 特殊関数ボタン
        st.markdown("##### 📐 関数・定数パッド")
        f1, f2, f3, f4, f5, f6 = st.columns(6)
        if f1.button("sin", key="calc_sin"): 
            st.session_state.calc_expr += "sin("
            st.rerun()
        if f2.button("cos", key="calc_cos"): 
            st.session_state.calc_expr += "cos("
            st.rerun()
        if f3.button("tan", key="calc_tan"): 
            st.session_state.calc_expr += "tan("
            st.rerun()
        if f4.button("sqrt", key="calc_sqrt"): 
            st.session_state.calc_expr += "sqrt("
            st.rerun()
        if f5.button("pi", key="calc_pi"): 
            st.session_state.calc_expr += "pi"
            st.rerun()
        if f6.button("log", key="calc_log"): 
            st.session_state.calc_expr += "log("
            st.rerun()

    with calc_tab2:
        st.subheader("設計用 単位換算")
        sub_conv = st.selectbox("換算ジャンル", ["力・荷重", "圧力", "トルク", "慣性モーメント"])
        
        if sub_conv == "力・荷重":
            val = st.number_input("入力値", value=100.0, key="f_val")
            unit = st.selectbox("単位", ["N", "kgf", "kN"])
            n_val = val if unit == "N" else (val * 9.80665 if unit == "kgf" else val * 1000.0)
            c1, c2, c3 = st.columns(3)
            c1.metric("N", f"{n_val:,.2f} N")
            c2.metric("kgf", f"{n_val / 9.80665:,.2f} kgf")
            c3.metric("kN", f"{n_val / 1000.0:,.4f} kN")
            
        elif sub_conv == "圧力":
            val = st.number_input("入力値", value=0.5, key="p_val")
            unit = st.selectbox("単位", ["MPa", "kPa", "bar", "kgf/cm²"])
            mpa_val = val if unit == "MPa" else (val / 1000.0 if unit == "kPa" else (val * 0.1 if unit == "bar" else val * 0.0980665))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("MPa", f"{mpa_val:.4f}")
            c2.metric("kPa", f"{mpa_val * 1000:,.1f}")
            c3.metric("bar", f"{mpa_val * 10:.3f}")
            c4.metric("kgf/cm²", f"{mpa_val / 0.0980665:.3f}")
            
        elif sub_conv == "トルク":
            val = st.number_input("入力値", value=1.0, key="t_val")
            unit = st.selectbox("単位", ["N·m", "N·cm", "kgf·cm", "kgf·m"])
            nm_val = val if unit == "N·m" else (val / 100.0 if unit == "N·cm" else (val * 0.0980665 if unit == "kgf·cm" else val * 9.80665))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("N·m", f"{nm_val:.4f}")
            c2.metric("N·cm", f"{nm_val * 100:.2f}")
            c3.metric("kgf·cm", f"{nm_val / 0.0980665:.2f}")
            c4.metric("kgf·m", f"{nm_val / 9.80665:.4f}")
            
        else:
            val = st.number_input("入力値", value=0.001, format="%.6f", key="j_val")
            unit = st.selectbox("単位", ["kg·m²", "kg·cm²", "g·cm²", "kgf·cm·s²"])
            kgm2_val = val if unit == "kg·m²" else (val * 1e-4 if unit == "kg·cm²" else (val * 1e-7 if unit == "g·cm²" else val * 0.0980665))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("kg·m²", f"{kgm2_val:.6f}")
            c2.metric("kg·cm²", f"{kgm2_val * 1e4:,.2f}")
            c3.metric("g·cm²", f"{kgm2_val * 1e7:,.0f}")
            c4.metric("kgf·cm·s²", f"{kgm2_val / 0.0980665:.6f}")

    with calc_tab3:
        st.subheader("複数数値の集計・統計分析")
        st.markdown("複数の数値をスペース、カンマ（`,`）、または改行区切りで入力してください。統計量の計算とデータ分布のグラフ化を行います。")

        # 入力エリア
        data_input = st.text_area("測定データ・数値入力", value="10.2, 10.5, 9.8, 10.1, 10.3, 10.0, 9.9, 10.4, 10.1, 10.2")

        if st.button("集計・グラフ化を実行"):
            try:
                # 入力文字列を数値のリストに変換（カンマやスペース、改行に対応）
                # 全角カンマやスペースも考慮して置換
                cleaned_input = data_input.replace("，", ",").replace("\n", ",")
                raw_list = [x.strip() for x in cleaned_input.split(",") if x.strip()]
                data_array = np.array([float(x) for x in raw_list])

                if len(data_array) == 0:
                    st.warning("有効な数値が入力されていません。")
                else:
                    # 統計量の計算
                    count = len(data_array)
                    total_sum = np.sum(data_array)
                    mean_val = np.mean(data_array)
                    std_val = np.std(data_array, ddof=1) if count > 1 else 0.0 # 不偏標準偏差
                    var_val = np.var(data_array, ddof=1) if count > 1 else 0.0
                    min_val = np.min(data_array)
                    max_val = np.max(data_array)
                    range_val = max_val - min_val

                    st.success("集計が完了しました！")

                    # メトリックで主要な統計量を表示
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("データ数 (n)", f"{count}")
                    m2.metric("合計値 (Sum)", f"{total_sum:,.3f}")
                    m3.metric("平均値 (Mean)", f"{mean_val:,.3f}")
                    m4.metric("標準偏差 (σ)", f"{std_val:,.3f}")

                    m5, m6, m7, m8 = st.columns(4)
                    m5.metric("分散", f"{var_val:,.3f}")
                    m6.metric("最小値 (Min)", f"{min_val:,.3f}")
                    m7.metric("最大値 (Max)", f"{max_val:,.3f}")
                    m8.metric("レンジ (Max-Min)", f"{range_val:,.3f}")

                    st.markdown("---")
                    st.markdown("### 📊 データ分布グラフ（ヒストグラム ＆ 推移）")

                    # グラフの描画（2つのサブプロット：ヒストグラムと折れ線推移）
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

                    # 1. ヒストグラム（データのばらつき・分布）
                    ax1.hist(data_array, bins='auto', color='#2563eb', edgecolor='white', alpha=0.8)
                    ax1.axvline(mean_val, color='red', linestyle='--', linewidth=1.5, label=f'Mean: {mean_val:.2f}')
                    ax1.set_title("Data Distribution (Histogram)", fontsize=11, fontweight='bold')
                    ax1.set_xlabel("Value")
                    ax1.set_ylabel("Frequency")
                    ax1.legend()
                    ax1.grid(True, linestyle='--', alpha=0.5)

                    # 2. シーケンスプロット（データの順番通りの推移）
                    ax2.plot(range(1, count + 1), data_array, marker='o', color='#16a34a', linewidth=2)
                    ax2.axhline(mean_val, color='red', linestyle='--', linewidth=1.5, label=f'Mean')
                    ax2.set_title("Sequence Plot", fontsize=11, fontweight='bold')
                    ax2.set_xlabel("Index / Order")
                    ax2.set_ylabel("Value")
                    ax2.legend()
                    ax2.grid(True, linestyle='--', alpha=0.5)

                    plt.tight_layout()
                    st.pyplot(fig)

            except ValueError:
                st.error("数値以外の文字が含まれているか、形式が正しくありません。半角の数値とカンマ、またはスペース・改行で入力してください。")
            except Exception as e:
                st.error(f"集計中にエラーが発生しました: {e}")

# ==========================================
# 4. 単語帳 カテゴリ（カテゴリ別保存・閲覧）
# ==========================================
elif main_category == "単語帳":
    st.title("設計単語帳・ナレッジベース")
    st.markdown("カテゴリ別に専門用語や設計のポイントを保存・閲覧できます。")

    dict_tab1, dict_tab2 = st.tabs(["用語の閲覧・検索", "新しい用語の追加"])

    with dict_tab1:
        selected_category = st.selectbox("カテゴリ絞り込み", ["すべて"] + list(st.session_state.dictionary_data.keys()))
        search_query = st.text_input("キーワード検索", "")

        for cat, terms in st.session_state.dictionary_data.items():
            if selected_category != "すべて" and selected_category != cat:
                continue
            
            filtered_terms = {t: d for t, d in terms.items() if search_query.lower() in t.lower() or search_query.lower() in d.lower()}
            
            if filtered_terms:
                st.markdown(f"### 📁 カテゴリ: {cat}")
                for term, desc in filtered_terms.items():
                    with st.expander(f"📖 {term}"):
                        st.write(desc)

    with dict_tab2:
        st.subheader("新しい単語・用語の登録")
        new_category = st.selectbox("登録先カテゴリ", list(st.session_state.dictionary_data.keys()) + ["新しいカテゴリを追加"])
        
        if new_category == "新しいカテゴリを追加":
            new_category_name = st.text_input("新しいカテゴリ名")
        else:
            new_category_name = new_category

        new_term = st.text_input("用語（タイトル）")
        new_desc = st.text_area("意味・解説")

        if st.button("単語を登録する"):
            if new_term and new_desc and new_category_name:
                if new_category_name not in st.session_state.dictionary_data:
                    st.session_state.dictionary_data[new_category_name] = {}
                st.session_state.dictionary_data[new_category_name][new_term] = new_desc
                st.success(f"「{new_term}」をカテゴリ「{new_category_name}」に登録しました！")
            else:
                st.warning("すべての項目を入力してください。")
