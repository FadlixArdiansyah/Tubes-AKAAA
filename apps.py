import streamlit as st
import random
import time
import sys
import matplotlib.pyplot as plt


st.set_page_config(page_title="Analisis Merge Sort", layout="wide")


sys.setrecursionlimit(10**7)

# --- STRUKTUR DATA ---
class Video:
    def __init__(self, title, views):
        self.title = title
        self.views = views

    def __repr__(self):
        return f"{{Title: {self.title}, Views: {self.views}}}"

# --- ALGORITMA MERGE SORT ---

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i].views < right[j].views:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def merge_sort_recursive(arr):
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    left = merge_sort_recursive(arr[:mid])
    right = merge_sort_recursive(arr[mid:])
    return merge(left, right)

def merge_sort_iterative(arr):
    arr_copy = arr[:] 
    width = 1
    n = len(arr_copy)
    while width < n:
        l = 0
        while l < n:
            r = min(l + (width * 2 - 1), n - 1)
            m = min(l + width - 1, n - 1)
            if m < r:
                left_part = arr_copy[l : m + 1]
                right_part = arr_copy[m + 1 : r + 1]
                merged = merge(left_part, right_part)
                arr_copy[l : r + 1] = merged
            l += width * 2
        width *= 2
    return arr_copy

# --- FUNGSI PARSING INPUT MANUAL ---
def parse_manual_input(text_input):
    data = []
    lines = text_input.strip().split('\n')
    errors = []
    for idx, line in enumerate(lines):
        try:
            parts = line.split(',')
            if len(parts) < 2:
                title = f"Data Manual #{idx+1}"
                views = int(parts[0].strip())
            else:
                title = parts[0].strip()
                views = int(parts[1].strip())
            data.append(Video(title, views))
        except ValueError:
            errors.append(f"Baris {idx+1} error: '{line}'")
    return data, errors

# --- USER INTERFACE ---

st.title("🔢 Analisis Kompleksitas Merge Sort")
st.markdown("Studi Kasus: **Pengurutan Video YouTube Berdasarkan Views**")
st.write("---")


st.sidebar.header("1. Pengaturan Data")


input_method = st.sidebar.radio("Pilih Sumber Data:", ["🎲 Generate Random (Acak)", "✍️ Input Manual"])

raw_data = []

if input_method == "🎲 Generate Random (Acak)":

    n = st.sidebar.number_input("Masukkan Jumlah Data (N):", min_value=10, value=1000, step=100)
    
    if st.sidebar.button("Generate Data"):
        for i in range(n):
            raw_data.append(Video(f"Video #{i+1}", random.randint(10, 1_000_000)))
        st.session_state['saved_data'] = raw_data
        st.sidebar.success(f"Berhasil membuat {n} data acak!")

elif input_method == "✍️ Input Manual":
    st.sidebar.info("Format: Judul, Views (per baris)")
    user_text = st.sidebar.text_area("Paste data di sini:", height=200, placeholder="Video A, 500\nVideo B, 1000")
    if st.sidebar.button("Load Data Manual"):
        parsed_data, parse_errors = parse_manual_input(user_text)
        if parse_errors:
            for err in parse_errors: st.sidebar.error(err)
        else:
            raw_data = parsed_data
            st.session_state['saved_data'] = raw_data
            st.sidebar.success(f"Berhasil load {len(raw_data)} data!")

# Load data dari session
if 'saved_data' in st.session_state:
    raw_data = st.session_state['saved_data']

# --- TAMPILAN UTAMA ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Preview Data")
    if len(raw_data) > 0:
        st.info(f"Total Data: {len(raw_data)}")
        preview_text = "\n".join([str(d) for d in raw_data])
        st.text_area("Isi Data", value=preview_text, height=300)
    else:
        st.warning("Data kosong. Silakan input di sidebar kiri.")

with col2:
    st.subheader("Hasil Analisis & Grafik")
    if len(raw_data) > 0:
        if st.button("🚀 Jalankan Benchmark"):
            progress = st.progress(0)
            status = st.empty()
            
            # 1. Rekursif
            status.text("Running Recursive...")
            start_rec = time.perf_counter()
            try:
                merge_sort_recursive(raw_data)
                end_rec = time.perf_counter()
                time_rec = (end_rec - start_rec) * 1000
            except RecursionError:
                time_rec = 0
                st.error("Stack Overflow (Rekursif Gagal)")
            progress.progress(50)
            
            # 2. Iteratif
            status.text("Running Iterative...")
            start_iter = time.perf_counter()
            merge_sort_iterative(raw_data)
            end_iter = time.perf_counter()
            time_iter = (end_iter - start_iter) * 1000
            progress.progress(100)
            status.text("Selesai!")
            
            # Tampilkan Angka
            c1, c2 = st.columns(2)
            c1.metric("Waktu Rekursif", f"{time_rec:.4f} ms")
            c2.metric("Waktu Iteratif", f"{time_iter:.4f} ms")
            
            # Tampilkan Grafik
            fig, ax = plt.subplots()
            ax.bar(['Rekursif', 'Iteratif'], [time_rec, time_iter], color=['red', 'blue'])
            ax.set_ylabel('Waktu (ms)')
            ax.set_title(f'Perbandingan N={len(raw_data)}')
            for i, v in enumerate([time_rec, time_iter]):
                ax.text(i, v, f"{v:.2f}", ha='center', va='bottom')
            st.pyplot(fig)
            
            # Kesimpulan Otomatis
            if time_rec > 0 and time_iter > 0:
                diff = abs(time_rec - time_iter)
                fastest = "Iteratif" if time_iter < time_rec else "Rekursif"
                st.success(f"Analisis: Algoritma **{fastest}** lebih cepat dengan selisih **{diff:.4f} ms**.")
    else:
        st.info("← Masukkan data dulu di sidebar.")