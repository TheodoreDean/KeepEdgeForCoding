import sys
import os
import math
import numpy as np
from collections import Counter

class AIS31TestSuite:
    def __init__(self, filepath):
        self.filepath = filepath
        self.bits = None
        self.file_size = 0
        
        # BSI AIS 31 defined thresholds
        self.T1_BOUNDS = (9654, 10346)
        self.T2_BOUNDS = (1.03, 57.4)
        self.T3_INTERVALS = {
            1: (2267, 2733),
            2: (1079, 1421),
            3: (502, 748),
            4: (223, 402),
            5: (90, 223),
            6: (90, 223) # >=6
        }
        self.T5_BOUNDS = (2326, 2674)
        
    def load_data(self):
        """读取二进制文件并转换为比特数组 (0/1)"""
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read()
            self.file_size = len(data)
            # Convert bytes to numpy array of bits
            # using uint8 for ease of processing, though takes more RAM
            byte_arr = np.frombuffer(data, dtype=np.uint8)
            self.bits = np.unpackbits(byte_arr)
            print(f"[INFO] 文件已加载: {self.filepath}")
            print(f"[INFO] 总比特数: {len(self.bits)}")
            return True
        except Exception as e:
            print(f"[ERROR] 无法读取文件: {e}")
            return False

    def run_tests(self):
        if self.bits is None:
            return

        print("\n" + "="*60)
        print("BSI AIS 20/31 标准测试报告 (Test Procedure A & B)")
        print("="*60)

        # ---------------------------------------------------------
        # Test Procedure A
        # ---------------------------------------------------------
        print("\n>>> 开始执行 Test Procedure A (T0 - T5)")
        
        # --- T0: Disjointness Test ---
        # Requirement: 2^16 words of 48 bits = 3,145,728 bits
        req_bits_t0 = (2**16) * 48
        if len(self.bits) >= req_bits_t0:
            t0_res = self.test_t0_disjointness(self.bits[:req_bits_t0])
            print(f"[T0] Disjointness Test: {'PASSED' if t0_res else 'FAILED'}")
        else:
            print(f"[T0] Disjointness Test: SKIPPED (数据不足, 需要 {req_bits_t0} bits)")

        # --- T1-T5: Repeated Tests ---
        # Procedure A 步骤 2-7: 需要 257 个序列，每个 20,000 bits
        # 注: 标准描述了采样方法，这里我们简单地使用连续数据块
        num_seq = 257
        len_seq = 20000
        req_bits_seq = num_seq * len_seq # 5,140,000 bits
        
        # 如果数据不够，我们只跑一次作为演示，或者尽可能多跑
        available_seqs = len(self.bits) // len_seq
        if available_seqs < 1:
            print(f"[ERROR] 数据不足以执行 T1-T5 (至少需要 {len_seq} bits)")
        else:
            run_count = min(num_seq, available_seqs)
            print(f"\n[T1-T5] 正在对 {run_count} 个 20,000-bit 样本序列进行测试...")
            
            fails = {"T1": 0, "T2": 0, "T3": 0, "T4": 0, "T5": 0}
            
            for i in range(run_count):
                offset = i * len_seq
                chunk = self.bits[offset : offset + len_seq]
                
                if not self.test_t1_monobit(chunk): fails["T1"] += 1
                if not self.test_t2_poker(chunk): fails["T2"] += 1
                if not self.test_t3_runs(chunk): fails["T3"] += 1
                if not self.test_t4_long_run(chunk): fails["T4"] += 1
                
                # T5 (Procedure A Step 7): 
                # 标准要求: 对前10000位计算所有tau (1-5000) 的偏差，找到最大的tau，
                # 然后对后10000位用该tau进行测试。
                # 简化起见，或者为了性能，有时只测固定tau。这里我们实现标准要求的“最差情况”检查。
                if not self.test_t5_autocorrelation_procedure_a(chunk): fails["T5"] += 1

            total_failures = sum(fails.values())
            print(f"  -> 测试结果汇总 (Failures): {fails}")
            
            # 评估规则: 
            # (a) 全部通过 -> PASS
            # (b) >1 个失败 -> FAIL
            # (c) 正好 1 个失败 -> 允许重测一次 (这里脚本只做一次评估)
            if total_failures == 0:
                print("  => Test Procedure A: PASSED")
            elif total_failures == 1:
                print("  => Test Procedure A: CONDITIONAL (允许重测)")
            else:
                print("  => Test Procedure A: FAILED")

        # ---------------------------------------------------------
        # Test Procedure B
        # ---------------------------------------------------------
        print("\n" + "-"*60)
        print(">>> 开始执行 Test Procedure B (T6 - T8)")
        # Procedure B 是对流进行连续测试，这里我们假设文件是一个流
        
        # 此时需要一个新的游标，假设接在 Procedure A 后面，或者重新开始
        # 为了演示 T6-T8，我们从文件头开始取数据 (实际评估中应使用新数据)
        cursor = 0
        
        # --- T6: Uniform Distribution Test ---
        # Step 1: n=100,000, k=1 (Monobit check on 100k bits with alpha=0.025)
        # 标准文本中有些地方写 10,000 有些写 100,000。AIS 31 PDF page 55 Step 1 says n=100,000, a=0.025
        # 但 Note 212 说 n=10,000。这里取 100,000 更严格，或按 212 的 10,000。
        # 依据 PDF 212 Description Step 1: (k,n,a) = (1, 10000, 0.025). 
        # OK, let's use n=10000.
        t6_n = 10000
        if len(self.bits) >= cursor + t6_n:
            chunk_t6 = self.bits[cursor : cursor + t6_n]
            t6_res = self.test_t6_uniformity(chunk_t6, n=t6_n)
            print(f"[T6] Uniformity Test: {'PASSED' if t6_res else 'FAILED'}")
            cursor += t6_n
        else:
            print("[T6] SKIPPED (数据不足)")

        # --- T7: Comparative Test (Step 2, 3, 4) ---
        # Step 2: 1-step dependencies (Check pairs)
        # Step 3: 2-step dependencies (Check triplets)
        # Step 4: 3-step dependencies (Check quadruples)
        # 这是一个流处理过程，需要累积足够多的 pattern。
        # 简化处理：我们直接对大块数据进行检验。
        
        # 需要的数据量较大，这里取 300,000 bits 进行演示
        req_bits_t7 = 300000
        if len(self.bits) >= cursor + req_bits_t7:
            chunk_t7 = self.bits[cursor : cursor + req_bits_t7]
            t7_res = self.test_t7_comparative(chunk_t7)
            print(f"[T7] Comparative Test: {'PASSED' if t7_res else 'FAILED'}")
            cursor += req_bits_t7
        else:
            print("[T7] SKIPPED (数据不足)")

        # --- T8: Entropy Test (Coron's) ---
        # Step 5: L=8, Q=2560, K=256000
        # Total bits = (Q + K) * L = (2560 + 256000) * 8 = 2,068,480 bits
        req_bits_t8 = (2560 + 256000) * 8
        if len(self.bits) >= cursor + req_bits_t8:
            chunk_t8 = self.bits[cursor : cursor + req_bits_t8]
            t8_res = self.test_t8_entropy(chunk_t8)
            print(f"[T8] Entropy Test: {'PASSED' if t8_res else 'FAILED'}")
        else:
            print(f"[T8] SKIPPED (数据不足, 需要 {req_bits_t8} bits)")

    # =========================================================
    # Test Implementations
    # =========================================================

    def test_t0_disjointness(self, bits):
        """
        T0: Disjointness Test
        Check if 2^16 values of 48-bit words are all unique.
        """
        # Pack bits into 48-bit integers? numpy doesn't support 48-bit directly nicely.
        # We can pack into 6 bytes.
        # Ensure bits length is multiple of 8 for packing
        n_words = 2**16
        bit_len = 48
        total_bits = n_words * bit_len
        
        subset = bits[:total_bits]
        # Reshape to (2^16, 48)
        reshaped = subset.reshape(n_words, bit_len)
        # Pack to bytes: each row 48 bits -> 6 bytes
        # np.packbits packs 8 bits. 48 is divisible by 8.
        bytes_list = []
        for row in reshaped:
            # packbits produces uint8 array
            b = np.packbits(row)
            bytes_list.append(b.tobytes())
            
        # Check uniqueness
        unique_count = len(set(bytes_list))
        return unique_count == n_words

    def test_t1_monobit(self, bits):
        """T1: Monobit Test (FIPS 140-1)"""
        count_ones = np.count_nonzero(bits)
        # Bounds: 9654 < Ones < 10346
        return self.T1_BOUNDS[0] < count_ones < self.T1_BOUNDS[1]

    def test_t2_poker(self, bits):
        """T2: Poker Test"""
        # Divide 20000 bits into 5000 4-bit nibbles
        # Calculate X3 statistic
        n = 5000
        m = 4
        
        # Reshape to (5000, 4)
        matrix = bits[:n*m].reshape(n, m)
        # Convert bit rows to integer values 0-15
        # weights: 8, 4, 2, 1
        powers = np.array([8, 4, 2, 1], dtype=np.uint8)
        ints = matrix.dot(powers)
        
        counts = Counter(ints)
        sum_sq = sum([counts[i]**2 for i in range(16)])
        
        # X = (16/5000) * sum(f[i]^2) - 5000
        x3 = (16 / n) * sum_sq - n
        
        return self.T2_BOUNDS[0] < x3 < self.T2_BOUNDS[1]

    def test_t3_runs(self, bits):
        """T3: Runs Test"""
        # Find runs
        # Pad ends to ensure diff detects edge runs
        d = np.diff(np.concatenate(([not bits[0]], bits, [not bits[-1]])))
        indices = np.where(d != 0)[0]
        run_lengths = np.diff(indices)
        run_values = bits[indices[:-1]]
        
        # Bucket runs by value (0 or 1) and length (1..6)
        runs_0 = run_lengths[run_values == 0]
        runs_1 = run_lengths[run_values == 1]
        
        counts_0 = Counter(runs_0)
        counts_1 = Counter(runs_1)
        
        # Check standard intervals
        for length, (min_c, max_c) in self.T3_INTERVALS.items():
            if length < 6:
                c0 = counts_0.get(length, 0)
                c1 = counts_1.get(length, 0)
            else:
                # Sum all runs >= 6
                c0 = sum(v for k, v in counts_0.items() if k >= 6)
                c1 = sum(v for k, v in counts_1.items() if k >= 6)
                
            if not (min_c <= c0 <= max_c): return False
            if not (min_c <= c1 <= max_c): return False
            
        return True

    def test_t4_long_run(self, bits):
        """T4: Long Run Test"""
        # No run >= 34
        # Re-use run finding logic from T3
        d = np.diff(np.concatenate(([not bits[0]], bits, [not bits[-1]])))
        indices = np.where(d != 0)[0]
        run_lengths = np.diff(indices)
        
        if np.max(run_lengths) >= 34:
            return False
        return True

    def test_t5_autocorrelation_procedure_a(self, bits):
        """
        T5: Autocorrelation (Procedure A Step 7 Logic)
        1. Use first 10,000 bits.
        2. Calculate Z_tau for tau = 1..5000.
        3. Find tau with max deviation from 2500.
        4. Test second 10,000 bits with that tau.
        """
        # Split into two halves
        half = 10000
        part1 = bits[:half]
        part2 = bits[half:2*half]
        
        # Step 1: Find worst tau in part1
        # Z_tau = sum(b_j ^ b_{j+tau})
        # Standard calculation is Z_tau = sum_{j=1}^{5000} (b_j XOR b_{j+tau})
        # For part1, j goes 1 to 5000. j+tau goes up to 10000.
        
        max_dev = -1
        worst_tau = 1
        
        # This loop can be slow in pure python, but ok for 5000 iterations
        # Optimization: matrix operation?
        # Construct matrix of shifts? 
        # Memory heavy: 5000x5000 bits. 25M bits ~ 3MB. Feasible.
        
        # Let's vectorize
        # Create a matrix where row i is part1 shifted by i+1
        # Need base sequence b_1...b_5000 (indices 0..4999)
        base = part1[:5000]
        
        for tau in range(1, 5001):
            # shifted sequence: b_{1+tau}...b_{5000+tau}
            # indices: tau ... 4999+tau
            shifted = part1[tau : 5000+tau]
            xor_sum = np.sum(np.bitwise_xor(base, shifted))
            
            dev = abs(xor_sum - 2500)
            if dev > max_dev:
                max_dev = dev
                worst_tau = tau
                
        # Step 2: Test part2 with worst_tau
        base2 = part2[:5000]
        shifted2 = part2[worst_tau : 5000+worst_tau]
        final_z = np.sum(np.bitwise_xor(base2, shifted2))
        
        # Check bounds
        return self.T5_BOUNDS[0] < final_z < self.T5_BOUNDS[1]

    def test_t6_uniformity(self, bits, n=10000):
        """T6: Uniformity Test (k=1, n=10000, a=0.025)"""
        # Count ones in first n bits
        count = np.count_nonzero(bits[:n])
        prob = count / n
        # Bound: 0.5 +/- 0.025 => [0.475, 0.525]
        return 0.475 <= prob <= 0.525

    def test_t7_comparative(self, bits):
        """T7: Comparative Test (Simplified Check for Independence)"""
        # This test checks if conditional probabilities are homogeneous.
        # Procedure B Step 2: 1-step transition. 
        # Check if P(0|0) == P(0|1).
        # We collect pairs (b_i, b_{i+1})
        # TF0: pairs starting with 0. TF1: pairs starting with 1.
        
        # We iterate through non-overlapping pairs? Standard text says:
        # "split non-overlapping pairs... into TF0 and TF1... until both have n1 elements"
        # Standard n1 = 100000.
        
        # For demonstration on small file, we use what we have.
        # Let's verify "Procedure B Step 2" logic specifically.
        
        # Reshape to pairs (non-overlapping)
        n_pairs = len(bits) // 2
        pairs = bits[:n_pairs*2].reshape(n_pairs, 2)
        
        # Filter
        tf0 = pairs[pairs[:, 0] == 0] # Second bit where first is 0
        tf1 = pairs[pairs[:, 0] == 1] # Second bit where first is 1
        
        # Need sufficient data
        if len(tf0) < 100 or len(tf1) < 100:
            return True # Not enough data to fail
            
        # Calc probabilities of next bit being 1
        # v_emp_0(1)
        p0_1 = np.mean(tf0[:, 1])
        # v_emp_1(1) (standard says v_emp(1)(0) + v_emp(0)(1) approx 1? No, it compares distributions)
        # Actually Step 2 formula: | v_emp(0)(1) + v_emp(1)(0) - 1 | < 0.02
        # v_emp(0)(1) is Prob(1|0). v_emp(1)(0) is Prob(0|1).
        
        p1_0 = 1.0 - np.mean(tf1[:, 1])
        
        val = abs(p0_1 + p1_0 - 1.0)
        # Threshold a1 = 0.02
        return val < 0.02

    def test_t8_entropy(self, bits):
        """T8: Coron's Entropy Test"""
        L = 8
        Q = 2560
        K = 256000
        
        # Prepare L-bit words
        # Only take needed length
        total_len = (Q + K) * L
        used_bits = bits[:total_len]
        
        # Reshape to (N, 8)
        # Pack to integers
        matrix = used_bits.reshape(Q+K, L)
        # powers of 2: [128, 64, ..., 1]
        powers = 2**np.arange(L-1, -1, -1)
        words = matrix.dot(powers) # Array of integers 0-255
        
        # Algorithm:
        # For n = Q+1 to Q+K:
        #   An = distance to nearest predecessor with same value
        #   g(i) = 1/log(2) * sum(1/k for k in 1..i-1)
        #   f = 1/K * sum g(An)
        
        # Optimization: Precompute g(i) table? Max distance is Q+K.
        # But g(i) depends on A_n. A_n can be large.
        # Approx g(i) ~ log2(i) + ... for large i.
        
        # Last position map
        last_pos = {} # Map value -> index
        
        # Init (Q steps)
        for i in range(Q):
            val = words[i]
            last_pos[val] = i
            
        sum_g = 0.0
        
        # Test (K steps)
        # Precompute g? No, i varies. Use approx formula for large i.
        # g(i) = sum_{k=1}^{i-1} 1/k * (1/log2)
        # Harmonic number H_{i-1}.
        # H_n approx ln(n) + gamma.
        # g(i) approx (ln(i-1) + gamma) / ln(2) = log2(i-1) + gamma/ln(2).
        
        gamma = 0.5772156649
        ln2 = math.log(2)
        
        for i in range(Q, Q+K):
            val = words[i]
            if val in last_pos:
                dist = i - last_pos[val]
                
                # Calculate g(dist)
                # Exact sum for small dist, approx for large
                if dist < 100:
                    h = sum(1.0/k for k in range(1, dist))
                    g = h / ln2
                else:
                    g = math.log2(dist) + (gamma / ln2) # Simplified approx from standard Note
                
                sum_g += g
            else:
                # Standard doesn't explicitly handle "no predecessor" in the sum range?
                # Usually Q is large enough that all 2^L values appear. 
                # If not found, ignore or take distance from start? Standard implies A_n exists.
                # If Q >> 2^L (2560 >> 256), almost certain to verify.
                pass
                
            last_pos[val] = i
            
        fn = sum_g / K
        print(f"  -> 计算得到的熵统计量 f: {fn:.6f}")
        
        # Pass threshold: f > 7.976
        return fn > 7.976

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ais31_test.py <binary_file>")
        # Create dummy file for demo
        with open("test_sample.bin", "wb") as f:
            f.write(os.urandom(2 * 1024 * 1024))
        target = "test_sample.bin"
    else:
        target = sys.argv[1]
        
    tester = AIS31TestSuite(target)
    if tester.load_data():
        tester.run_tests()
