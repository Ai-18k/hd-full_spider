crypto = require("crypto")

window = globalThis;
navigator = {
    appName: 'Netscape'
}

!function(ab) {
    var ag = {};
    function i(ad) {
        if (ag[ad]) return ag[ad].exports;
        var t = ag[ad] = {
          i: ad,
          l: !1,
          exports: {}
        };
        return ab[ad].call(t.exports, t, t.exports, i), t.l = !0, t.exports;
    }
    return i.m = ab, i.c = ag, i.d = function (ab, ac, ad) {
        i.o(ab, ac) || Object.defineProperty(ab, ac, {
          enumerable: !0,
          get: ad
        });
      }, i.r = function (ab) {
        "undefined" != typeof Symbol && Symbol.toStringTag && Object.defineProperty(ab, Symbol.toStringTag, {
          value: "Module"
        }), Object.defineProperty(ab, "__esModule", {
          value: !0
        });
      }, i.t = function (ab, ac) {
        if (1 & ac && (ab = i(ab)), 8 & ac) return ab;
        if (4 & ac && "object" == typeof ab && ab && ab.$_ER) return ab;
        var ah = Object.create(null);
        if (i.r(ah), Object.defineProperty(ah, "default", {
          enumerable: !0,
          value: ab
        }), 2 & ac && "string" != typeof ab) for (var n in ab) i.d(ah, n, function (ac) {
          return ab[ac];
        }.bind(null, n));
        return ah;
      }, i.n = function (ab) {
        var ag = ab && ab.$_ER ? function () {
          return ab.default;
        } : function () {
          return ab;
        };
        return i.d(ag, "a", ag), ag;
      }, i.o = function (ab, ac) {
        return Object.prototype.hasOwnProperty.call(ab, ac);
      }, i.p = "",
    window.loader = i;
}({
    33: function (ab, ac, ad) {
      "use strict";
      ac.$_ER = !0, ac.default = void 0;
      var ai = function () {
        var af,
          ag = Object.create || function () {
            function s() {}
            return function (ab) {
              var ag;
              return s.prototype = ab, ag = new s(), s.prototype = null, ag;
            };
          }(),
          t = {},
          ah = t.lib = {},
          ai = ah.Base = {
            extend: function (ab) {
              var ah = ag(this);
              return ab && ah.mixIn(ab), ah.hasOwnProperty("init") && this.init !== ah.init || (ah.init = function () {
                ah.$super.init.apply(this, arguments);
              }), (ah.init.prototype = ah).$super = this, ah;
            },
            create: function () {
              var af = this.extend();
              return af.init.apply(af, arguments), af;
            },
            init: function () {},
            mixIn: function (ab) {
              for (var t in ab) ab.hasOwnProperty(t) && (this[t] = ab[t]);
              ab.hasOwnProperty("toString") && (this.toString = ab.toString);
            }
          },
          aj = ah.WordArray = ai.extend({
            init: function (ab, ac) {
              ab = this.words = ab || [], ac != undefined ? this.sigBytes = ac : this.sigBytes = 4 * ab.length;
            },
            concat: function (ab) {
              var ag = this.words,
                ah = ab.words,
                ai = this.sigBytes,
                aj = ab.sigBytes;
              if (this.clamp(), ai % 4) for (var r = 0; r < aj; r++) {
                var o = ah[r >>> 2] >>> 24 - r % 4 * 8 & 255;
                ag[ai + r >>> 2] |= o << 24 - (ai + r) % 4 * 8;
              } else for (r = 0; r < aj; r += 4) ag[ai + r >>> 2] = ah[r >>> 2];
              return this.sigBytes += aj, this;
            },
            clamp: function () {
              var af = this.words,
                ag = this.sigBytes;
              af[ag >>> 2] &= 4294967295 << 32 - ag % 4 * 8, af.length = Math.ceil(ag / 4);
            }
          }),
          r = t.enc = {},
          ba = r.Latin1 = {
            parse: function (ab) {
              for (var t = ab.length, s = [], n = 0; n < t; n++) s[n >>> 2] |= (255 & ab.charCodeAt(n)) << 24 - n % 4 * 8;
              return new aj.init(s, t);
            }
          },
          o = r.Utf8 = {
            parse: function (ab) {
              return ba.parse(unescape(encodeURIComponent(ab)));
            }
          },
          bb = ah.BufferedBlockAlgorithm = ai.extend({
            reset: function () {
              this.$_JBs = new aj.init(), this.$_BDFk = 0;
            },
            $_BDGI: function (ab) {
              "string" == typeof ab && (ab = o.parse(ab)), this.$_JBs.concat(ab), this.$_BDFk += ab.sigBytes;
            },
            $_BDHa: function (ab) {
              var ag = this.$_JBs,
                ah = ag.words,
                ai = ag.sigBytes,
                ba = this.blockSize,
                bb = ai / (4 * ba),
                bc = (bb = ab ? Math.ceil(bb) : Math.max((0 | bb) - this.$_BDId, 0)) * ba,
                bd = Math.min(4 * bc, ai);
              if (bc) {
                for (var _ = 0; _ < bc; _ += ba) this.$_BDJm(ah, _);
                var u = ah.splice(0, bc);
                ag.sigBytes -= bd;
              }
              return new aj.init(u, bd);
            },
            $_BDId: 0
          }),
          _ = t.algo = {},
          u = ah.Cipher = bb.extend({
            cfg: ai.extend(),
            createEncryptor: function (ab, ac) {
              return this.create(this.$_BEAQ, ab, ac);
            },
            init: function (ab, ac, ad) {
              this.cfg = this.cfg.extend(ad), this.$_BEBb = ab, this.$_BECH = ac, this.reset();
            },
            reset: function () {
              bb.reset.call(this), this.$_BEDx();
            },
            process: function (ab) {
              return this.$_BDGI(ab), this.$_BDHa();
            },
            finalize: function (ab) {
              return ab && this.$_BDGI(ab), this.$_BEEy();
            },
            keySize: 4,
            ivSize: 4,
            $_BEAQ: 1,
            $_BEFf: 2,
            $_BEGB: function (ab) {
              return {
                encrypt: function (ac, ad, ae) {
                  ad = ba.parse(ad), ae && ae.iv || ((ae = ae || {}).iv = ba.parse("0000000000000000"));
                  for (var n = v.encrypt(ab, ac, ad, ae), i = n.ciphertext.words, r = n.ciphertext.sigBytes, o = [], a = 0; a < r; a++) {
                    var _ = i[a >>> 2] >>> 24 - a % 4 * 8 & 255;
                    o.push(_);
                  }
                  return o;
                }
              };
            }
          }),
          bc = t.mode = {},
          bd = ah.BlockCipherMode = ai.extend({
            createEncryptor: function (ab, ac) {
              return this.Encryptor.create(ab, ac);
            },
            init: function (ab, ac) {
              this.$_BEHo = ab, this.$_BEIp = ac;
            }
          }),
          bf = bc.CBC = ((af = bd.extend()).Encryptor = af.extend({
            processBlock: function (ab, ac) {
              var ah = this.$_BEHo,
                ai = ah.blockSize;
              (function ab(ac, ad, ae) {
                var aj = this.$_BEIp;
                if (aj) {
                  var i = aj;
                  this.$_BEIp = undefined;
                } else var i = this.$_BEJg;
                for (var r = 0; r < ae; r++) ac[ad + r] ^= i[r];
              }).call(this, ab, ac, ai), ah.encryptBlock(ab, ac), this.$_BEJg = ab.slice(ac, ac + ai);
            }
          }), af),
          be = (t.pad = {}).Pkcs7 = {
            pad: function (ab, ac) {
              for (var s = 4 * ac, n = s - ab.sigBytes % s, i = n << 24 | n << 16 | n << 8 | n, r = [], o = 0; o < n; o += 4) r.push(i);
              var ah = aj.create(r, n);
              ab.concat(ah);
            }
          },
          bg = ah.BlockCipher = u.extend({
            cfg: u.cfg.extend({
              mode: bf,
              padding: be
            }),
            reset: function () {
              u.reset.call(this);
              var af = this.cfg,
                ag = af.iv,
                ah = af.mode;
              if (this.$_BEBb == this.$_BEAQ) var ai = ah.createEncryptor;
              this.$_BFAN && this.$_BFAN.$_BFBy == ai ? this.$_BFAN.init(this, ag && ag.words) : (this.$_BFAN = ai.call(ah, this, ag && ag.words), this.$_BFAN.$_BFBy = ai);
            },
            $_BDJm: function (ab, ac) {
              this.$_BFAN.processBlock(ab, ac);
            },
            $_BEEy: function () {
              var af = this.cfg.padding;
              if (this.$_BEBb == this.$_BEAQ) {
                af.pad(this.$_JBs, this.blockSize);
                var t = this.$_BDHa(!0);
              }
              return t;
            },
            blockSize: 4
          }),
          bh = ah.CipherParams = ai.extend({
            init: function (ab) {
              this.mixIn(ab);
            }
          }),
          v = ah.SerializableCipher = ai.extend({
            cfg: ai.extend(),
            encrypt: function (ab, ac, ad, ae) {
              ae = this.cfg.extend(ae);
              var aj = ab.createEncryptor(ad, ae),
                ba = aj.finalize(ac),
                bb = aj.cfg;
              return bh.create({
                ciphertext: ba,
                key: ad,
                iv: bb.iv,
                algorithm: ab,
                mode: bb.mode,
                padding: bb.padding,
                blockSize: ab.blockSize,
                formatter: ae.format
              });
            }
          }),
          bi = [],
          bj = [],
          ca = [],
          cb = [],
          cc = [],
          cd = [],
          ce = [],
          cf = [],
          cg = [],
          ch = [];
        !function () {
          for (var e = [], t = 0; t < 256; t++) e[t] = t < 128 ? t << 1 : t << 1 ^ 283;
          var af = 0,
            ag = 0;
          for (t = 0; t < 256; t++) {
            var i = ag ^ ag << 1 ^ ag << 2 ^ ag << 3 ^ ag << 4;
            i = i >>> 8 ^ 255 & i ^ 99, bi[af] = i;
            var r = e[bj[i] = af],
              o = e[r],
              a = e[o],
              _ = 257 * e[i] ^ 16843008 * i;
            ca[af] = _ << 24 | _ >>> 8, cb[af] = _ << 16 | _ >>> 16, cc[af] = _ << 8 | _ >>> 24, cd[af] = _;
            _ = 16843009 * a ^ 65537 * o ^ 257 * r ^ 16843008 * af;
            ce[i] = _ << 24 | _ >>> 8, cf[i] = _ << 16 | _ >>> 16, cg[i] = _ << 8 | _ >>> 24, ch[i] = _, af ? (af = r ^ e[e[e[a ^ r]]], ag ^= e[e[ag]]) : af = ag = 1;
          }
        }();
        var ci = [0, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54],
          cj = _.AES = bg.extend({
            $_BEDx: function () {
              if (!this.$_BFCQ || this.$_BFDK !== this.$_BECH) {
                for (var e = this.$_BFDK = this.$_BECH, t = e.words, s = e.sigBytes / 4, n = 4 * (1 + (this.$_BFCQ = 6 + s)), i = this.$_BFEg = [], r = 0; r < n; r++) if (r < s) i[r] = t[r];else {
                  var o = i[r - 1];
                  r % s ? 6 < s && r % s == 4 && (o = bi[o >>> 24] << 24 | bi[o >>> 16 & 255] << 16 | bi[o >>> 8 & 255] << 8 | bi[255 & o]) : (o = bi[(o = o << 8 | o >>> 24) >>> 24] << 24 | bi[o >>> 16 & 255] << 16 | bi[o >>> 8 & 255] << 8 | bi[255 & o], o ^= ci[r / s | 0] << 24), i[r] = i[r - s] ^ o;
                }
                for (var a = this.$_BFFs = [], _ = 0; _ < n; _++) {
                  r = n - _;
                  if (_ % 4) o = i[r];else o = i[r - 4];
                  a[_] = _ < 4 || r <= 4 ? o : ce[bi[o >>> 24]] ^ cf[bi[o >>> 16 & 255]] ^ cg[bi[o >>> 8 & 255]] ^ ch[bi[255 & o]];
                }
              }
            },
            encryptBlock: function (ab, ac) {
              this.$_BFGx(ab, ac, this.$_BFEg, ca, cb, cc, cd, bi);
            },
            $_BFGx: function (ab, ac, ad, ae, af, ag, ah, ai) {
              for (var _ = this.$_BFCQ, u = ab[ac] ^ ad[0], c = ab[ac + 1] ^ ad[1], h = ab[ac + 2] ^ ad[2], p = ab[ac + 3] ^ ad[3], l = 4, f = 1; f < _; f++) {
                var d = ae[u >>> 24] ^ af[c >>> 16 & 255] ^ ag[h >>> 8 & 255] ^ ah[255 & p] ^ ad[l++],
                  g = ae[c >>> 24] ^ af[h >>> 16 & 255] ^ ag[p >>> 8 & 255] ^ ah[255 & u] ^ ad[l++],
                  m = ae[h >>> 24] ^ af[p >>> 16 & 255] ^ ag[u >>> 8 & 255] ^ ah[255 & c] ^ ad[l++],
                  v = ae[p >>> 24] ^ af[u >>> 16 & 255] ^ ag[c >>> 8 & 255] ^ ah[255 & h] ^ ad[l++];
                u = d, c = g, h = m, p = v;
              }
              d = (ai[u >>> 24] << 24 | ai[c >>> 16 & 255] << 16 | ai[h >>> 8 & 255] << 8 | ai[255 & p]) ^ ad[l++], g = (ai[c >>> 24] << 24 | ai[h >>> 16 & 255] << 16 | ai[p >>> 8 & 255] << 8 | ai[255 & u]) ^ ad[l++], m = (ai[h >>> 24] << 24 | ai[p >>> 16 & 255] << 16 | ai[u >>> 8 & 255] << 8 | ai[255 & c]) ^ ad[l++], v = (ai[p >>> 24] << 24 | ai[u >>> 16 & 255] << 16 | ai[c >>> 8 & 255] << 8 | ai[255 & h]) ^ ad[l++];
              ab[ac] = d, ab[ac + 1] = g, ab[ac + 2] = m, ab[ac + 3] = v;
            },
            keySize: 8
          });
        return t.AES = bg.$_BEGB(cj), t.AES;
      }();
      ac.default = ai;
    },
    34: function (ab, ac, ad) {
      "use strict";
      ac.$_ER = !0, ac.default = void 0;
      var ai = function () {
        function af() {
          this.i = 0, this.j = 0, this.S = [];
        }
        af.prototype.init = function ab(ac) {
          var ah, ai, aj;
          for (ah = 0; ah < 256; ++ah) this.S[ah] = ah;
          for (ah = ai = 0; ah < 256; ++ah) ai = ai + this.S[ah] + ac[ah % ac.length] & 255, aj = this.S[ah], this.S[ah] = this.S[ai], this.S[ai] = aj;
          this.i = 0, this.j = 0;
        }, af.prototype.next = function ab() {
          var ag;
          return this.i = this.i + 1 & 255, this.j = this.j + this.S[this.i] & 255, ag = this.S[this.i], this.S[this.i] = this.S[this.j], this.S[this.j] = ag, this.S[ag + this.S[this.i] & 255];
        };
        var n,
          ag,
          ah,
          t,
          ai = 256;
        if (null == ag) {
          var a;
          if (ag = [], ah = 0, window.crypto && window.crypto.getRandomValues) {
            var _ = new Uint32Array(256);
            for (window.crypto.getRandomValues(_), a = 0; a < _.length; ++a) ag[ah++] = 255 & _[a];
          }
          var u = 0,
            c = function ab(ac) {
              if (256 <= (u = u || 0) || ai <= ah) window.removeEventListener ? (u = 0, window.removeEventListener("mousemove", ab, !1)) : window.detachEvent && (u = 0, window.detachEvent("onmousemove", ab));else try {
                var s = ac.x + ac.y;
                ag[ah++] = 255 & s, u += 1;
              } catch (e) {}
            };
          window.addEventListener ? window.addEventListener("mousemove", c, !1) : window.attachEvent && window.attachEvent("onmousemove", c);
        }
        function h() {
          if (null == n) {
            n = function ab() {
              return new af();
            }();
            while (ah < ai) {
              var e = Math.floor(65536 * Math.random());
              ag[ah++] = 255 & e;
            }
            for (n.init(ag), ah = 0; ah < ag.length; ++ah) ag[ah] = 0;
            ah = 0;
          }
          return n.next();
        }
        function aj() {}
        aj.prototype.nextBytes = function ab(ac) {
          var ah;
          for (ah = 0; ah < ac.length; ++ah) ac[ah] = h();
        };
        function b(ac, ae, af) {
          null != ac && ("number" == typeof ac ? this.fromNumber(ac, ae, af) : null == ae && "string" != typeof ac ? this.fromString(ac, 256) : this.fromString(ac, ae));
        }
        function w() {
          return new b(null);
        }
        t = "Microsoft Internet Explorer" == navigator.appName ? (b.prototype.am = function ab(ac, ad, ae, af, ag, ah) {
          var bc = 32767 & ad,
            bd = ad >> 15;
          while (0 <= --ah) {
            var _ = 32767 & this[ac],
              u = this[ac++] >> 15,
              c = bd * _ + u * bc;
            ag = ((_ = bc * _ + ((32767 & c) << 15) + ae[af] + (1073741823 & ag)) >>> 30) + (c >>> 15) + bd * u + (ag >>> 30), ae[af++] = 1073741823 & _;
          }
          return ag;
        }, 30) : "Netscape" != navigator.appName ? (b.prototype.am = function ab(ac, ad, ae, af, ag, ah) {
          while (0 <= --ah) {
            var o = ad * this[ac++] + ae[af] + ag;
            ag = Math.floor(o / 67108864), ae[af++] = 67108863 & o;
          }
          return ag;
        }, 26) : (b.prototype.am = function ab(ac, ad, ae, af, ag, ah) {
          var bc = 16383 & ad,
            bd = ad >> 14;
          while (0 <= --ah) {
            var _ = 16383 & this[ac],
              u = this[ac++] >> 14,
              c = bd * _ + u * bc;
            ag = ((_ = bc * _ + ((16383 & c) << 14) + ae[af] + ag) >> 28) + (c >> 14) + bd * u, ae[af++] = 268435455 & _;
          }
          return ag;
        }, 28), b.prototype.DB = t, b.prototype.DM = (1 << t) - 1, b.prototype.DV = 1 << t;
        b.prototype.FV = Math.pow(2, 52), b.prototype.F1 = 52 - t, b.prototype.F2 = 2 * t - 52;
        var ba,
          bb,
          bc = "0123456789abcdefghijklmnopqrstuvwxyz",
          bd = [];
        for (ba = "0".charCodeAt(0), bb = 0; bb <= 9; ++bb) bd[ba++] = bb;
        for (ba = "a".charCodeAt(0), bb = 10; bb < 36; ++bb) bd[ba++] = bb;
        for (ba = "A".charCodeAt(0), bb = 10; bb < 36; ++bb) bd[ba++] = bb;
        function m(ab) {
          return bc.charAt(ab);
        }
        function v(ac) {
          var t = w();
          return t.fromInt(ac), t;
        }
        function y(ab) {
          var t,
            s = 1;
          return 0 != (t = ab >>> 16) && (ab = t, s += 16), 0 != (t = ab >> 8) && (ab = t, s += 8), 0 != (t = ab >> 4) && (ab = t, s += 4), 0 != (t = ab >> 2) && (ab = t, s += 2), 0 != (t = ab >> 1) && (ab = t, s += 1), s;
        }
        function bf(ac) {
          this.m = ac;
        }
        function be(ac) {
          this.m = ac, this.mp = ac.invDigit(), this.mpl = 32767 & this.mp, this.mph = this.mp >> 15, this.um = (1 << ac.DB - 15) - 1, this.mt2 = 2 * ac.t;
        }
        function bg() {
          this.n = null, this.e = 0, this.d = null, this.p = null, this.q = null, this.dmp1 = null, this.dmq1 = null, this.coeff = null;
          this.setPublic("00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D9451F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D686D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81", "10001");
        }
        return bf.prototype.convert = function ab(ac) {
          return ac.s < 0 || 0 <= ac.compareTo(this.m) ? ac.mod(this.m) : ac;
        }, bf.prototype.revert = function ab(ac) {
          return ac;
        }, bf.prototype.reduce = function ab(ac) {
          ac.divRemTo(this.m, null, ac);
        }, bf.prototype.mulTo = function ab(ac, ad, ae) {
          ac.multiplyTo(ad, ae), this.reduce(ae);
        }, bf.prototype.sqrTo = function ab(ac, ad) {
          ac.squareTo(ad), this.reduce(ad);
        }, be.prototype.convert = function ab(ac) {
          var ah = w();
          return ac.abs().dlShiftTo(this.m.t, ah), ah.divRemTo(this.m, null, ah), ac.s < 0 && 0 < ah.compareTo(b.ZERO) && this.m.subTo(ah, ah), ah;
        }, be.prototype.revert = function ab(ac) {
          var ah = w();
          return ac.copyTo(ah), this.reduce(ah), ah;
        }, be.prototype.reduce = function ab(ac) {
          while (ac.t <= this.mt2) ac[ac.t++] = 0;
          for (var t = 0; t < this.m.t; ++t) {
            var s = 32767 & ac[t],
              n = s * this.mpl + ((s * this.mph + (ac[t] >> 15) * this.mpl & this.um) << 15) & ac.DM;
            ac[s = t + this.m.t] += this.m.am(0, n, ac, t, 0, this.m.t);
            while (ac[s] >= ac.DV) ac[s] -= ac.DV, ac[++s]++;
          }
          ac.clamp(), ac.drShiftTo(this.m.t, ac), 0 <= ac.compareTo(this.m) && ac.subTo(this.m, ac);
        }, be.prototype.mulTo = function ab(ac, ad, ae) {
          ac.multiplyTo(ad, ae), this.reduce(ae);
        }, be.prototype.sqrTo = function ab(ac, ad) {
          ac.squareTo(ad), this.reduce(ad);
        }, b.prototype.copyTo = function ab(ac) {
          for (var t = this.t - 1; 0 <= t; --t) ac[t] = this[t];
          ac.t = this.t, ac.s = this.s;
        }, b.prototype.fromInt = function ab(ac) {
          this.t = 1, this.s = ac < 0 ? -1 : 0, 0 < ac ? this[0] = ac : ac < -1 ? this[0] = ac + this.DV : this.t = 0;
        }, b.prototype.fromString = function ab(ac, ad) {
          var ai;
          if (16 == ad) ai = 4;else if (8 == ad) ai = 3;else if (256 == ad) ai = 8;else if (2 == ad) ai = 1;else if (32 == ad) ai = 5;else {
            if (4 != ad) return void this.fromRadix(ac, ad);
            ai = 2;
          }
          this.t = 0, this.s = 0;
          var aj,
            ba,
            bb = ac.length,
            bc = !1,
            bf = 0;
          while (0 <= --bb) {
            var _ = 8 == ai ? 255 & ac[bb] : (aj = bb, null == (ba = bd[ac.charCodeAt(aj)]) ? -1 : ba);
            _ < 0 ? "-" == ac.charAt(bb) && (bc = !0) : (bc = !1, 0 == bf ? this[this.t++] = _ : bf + ai > this.DB ? (this[this.t - 1] |= (_ & (1 << this.DB - bf) - 1) << bf, this[this.t++] = _ >> this.DB - bf) : this[this.t - 1] |= _ << bf, (bf += ai) >= this.DB && (bf -= this.DB));
          }
          8 == ai && 0 != (128 & ac[0]) && (this.s = -1, 0 < bf && (this[this.t - 1] |= (1 << this.DB - bf) - 1 << bf)), this.clamp(), bc && b.ZERO.subTo(this, this);
        }, b.prototype.clamp = function ab() {
          var ag = this.s & this.DM;
          while (0 < this.t && this[this.t - 1] == ag) --this.t;
        }, b.prototype.dlShiftTo = function ab(ac, ad) {
          var ai;
          for (ai = this.t - 1; 0 <= ai; --ai) ad[ai + ac] = this[ai];
          for (ai = ac - 1; 0 <= ai; --ai) ad[ai] = 0;
          ad.t = this.t + ac, ad.s = this.s;
        }, b.prototype.drShiftTo = function ab(ac, ad) {
          for (var s = ac; s < this.t; ++s) ad[s - ac] = this[s];
          ad.t = Math.max(this.t - ac, 0), ad.s = this.s;
        }, b.prototype.lShiftTo = function ab(ac, ad) {
          var ai,
            aj = ac % this.DB,
            ba = this.DB - aj,
            bb = (1 << ba) - 1,
            bc = Math.floor(ac / this.DB),
            bd = this.s << aj & this.DM;
          for (ai = this.t - 1; 0 <= ai; --ai) ad[ai + bc + 1] = this[ai] >> ba | bd, bd = (this[ai] & bb) << aj;
          for (ai = bc - 1; 0 <= ai; --ai) ad[ai] = 0;
          ad[bc] = bd, ad.t = this.t + bc + 1, ad.s = this.s, ad.clamp();
        }, b.prototype.rShiftTo = function ab(ac, ad) {
          ad.s = this.s;
          var ai = Math.floor(ac / this.DB);
          if (ai >= this.t) ad.t = 0;else {
            var n = ac % this.DB,
              i = this.DB - n,
              r = (1 << n) - 1;
            ad[0] = this[ai] >> n;
            for (var o = ai + 1; o < this.t; ++o) ad[o - ai - 1] |= (this[o] & r) << i, ad[o - ai] = this[o] >> n;
            0 < n && (ad[this.t - ai - 1] |= (this.s & r) << i), ad.t = this.t - ai, ad.clamp();
          }
        }, b.prototype.subTo = function ab(ac, ad) {
          var ai = 0,
            aj = 0,
            ba = Math.min(ac.t, this.t);
          while (ai < ba) aj += this[ai] - ac[ai], ad[ai++] = aj & this.DM, aj >>= this.DB;
          if (ac.t < this.t) {
            aj -= ac.s;
            while (ai < this.t) aj += this[ai], ad[ai++] = aj & this.DM, aj >>= this.DB;
            aj += this.s;
          } else {
            aj += this.s;
            while (ai < ac.t) aj -= ac[ai], ad[ai++] = aj & this.DM, aj >>= this.DB;
            aj -= ac.s;
          }
          ad.s = aj < 0 ? -1 : 0, aj < -1 ? ad[ai++] = this.DV + aj : 0 < aj && (ad[ai++] = aj), ad.t = ai, ad.clamp();
        }, b.prototype.multiplyTo = function ab(ac, ad) {
          var ai = this.abs(),
            aj = ac.abs(),
            ba = ai.t;
          ad.t = ba + aj.t;
          while (0 <= --ba) ad[ba] = 0;
          for (ba = 0; ba < aj.t; ++ba) ad[ba + ai.t] = ai.am(0, aj[ba], ad, ba, 0, ai.t);
          ad.s = 0, ad.clamp(), this.s != ac.s && b.ZERO.subTo(ad, ad);
        }, b.prototype.squareTo = function ab(ac) {
          var ah = this.abs(),
            ai = ac.t = 2 * ah.t;
          while (0 <= --ai) ac[ai] = 0;
          for (ai = 0; ai < ah.t - 1; ++ai) {
            var n = ah.am(ai, ah[ai], ac, 2 * ai, 0, 1);
            (ac[ai + ah.t] += ah.am(ai + 1, 2 * ah[ai], ac, 2 * ai + 1, n, ah.t - ai - 1)) >= ah.DV && (ac[ai + ah.t] -= ah.DV, ac[ai + ah.t + 1] = 1);
          }
          0 < ac.t && (ac[ac.t - 1] += ah.am(ai, ah[ai], ac, 2 * ai, 0, 1)), ac.s = 0, ac.clamp();
        }, b.prototype.divRemTo = function ab(ac, ad, ae) {
          var aj = ac.abs();
          if (!(aj.t <= 0)) {
            var i = this.abs();
            if (i.t < aj.t) return null != ad && ad.fromInt(0), void (null != ae && this.copyTo(ae));
            null == ae && (ae = w());
            var r = w(),
              o = this.s,
              a = ac.s,
              _ = this.DB - y(aj[aj.t - 1]);
            0 < _ ? (aj.lShiftTo(_, r), i.lShiftTo(_, ae)) : (aj.copyTo(r), i.copyTo(ae));
            var u = r.t,
              c = r[u - 1];
            if (0 != c) {
              var h = c * (1 << this.F1) + (1 < u ? r[u - 2] >> this.F2 : 0),
                p = this.FV / h,
                l = (1 << this.F1) / h,
                f = 1 << this.F2,
                d = ae.t,
                g = d - u,
                m = null == ad ? w() : ad;
              r.dlShiftTo(g, m), 0 <= ae.compareTo(m) && (ae[ae.t++] = 1, ae.subTo(m, ae)), b.ONE.dlShiftTo(u, m), m.subTo(r, r);
              while (r.t < u) r[r.t++] = 0;
              while (0 <= --g) {
                var v = ae[--d] == c ? this.DM : Math.floor(ae[d] * p + (ae[d - 1] + f) * l);
                if ((ae[d] += r.am(0, v, ae, g, 0, u)) < v) {
                  r.dlShiftTo(g, m), ae.subTo(m, ae);
                  while (ae[d] < --v) ae.subTo(m, ae);
                }
              }
              null != ad && (ae.drShiftTo(u, ad), o != a && b.ZERO.subTo(ad, ad)), ae.t = u, ae.clamp(), 0 < _ && ae.rShiftTo(_, ae), o < 0 && b.ZERO.subTo(ae, ae);
            }
          }
        }, b.prototype.invDigit = function ab() {
          if (this.t < 1) return 0;
          var ag = this[0];
          if (0 == (1 & ag)) return 0;
          var ah = 3 & ag;
          return 0 < (ah = (ah = (ah = (ah = ah * (2 - (15 & ag) * ah) & 15) * (2 - (255 & ag) * ah) & 255) * (2 - ((65535 & ag) * ah & 65535)) & 65535) * (2 - ag * ah % this.DV) % this.DV) ? this.DV - ah : -ah;
        }, b.prototype.isEven = function ab() {
          return 0 == (0 < this.t ? 1 & this[0] : this.s);
        }, b.prototype.exp = function ab(ac, ad) {
          if (4294967295 < ac || ac < 1) return b.ONE;
          var ai = w(),
            aj = w(),
            ba = ad.convert(this),
            bb = y(ac) - 1;
          ba.copyTo(ai);
          while (0 <= --bb) if (ad.sqrTo(ai, aj), 0 < (ac & 1 << bb)) ad.mulTo(aj, ba, ai);else {
            var o = ai;
            ai = aj, aj = o;
          }
          return ad.revert(ai);
        }, b.prototype.toString = function ab(ac) {
          if (this.s < 0) return "-" + this.negate().toString(ac);
          var ah;
          if (16 == ac) ah = 4;else if (8 == ac) ah = 3;else if (2 == ac) ah = 1;else if (32 == ac) ah = 5;else {
            if (4 != ac) return this.toRadix(ac);
            ah = 2;
          }
          var ai,
            aj = (1 << ah) - 1,
            ba = !1,
            bb = "",
            bc = this.t,
            bd = this.DB - bc * this.DB % ah;
          if (0 < bc--) {
            bd < this.DB && 0 < (ai = this[bc] >> bd) && (ba = !0, bb = m(ai));
            while (0 <= bc) bd < ah ? (ai = (this[bc] & (1 << bd) - 1) << ah - bd, ai |= this[--bc] >> (bd += this.DB - ah)) : (ai = this[bc] >> (bd -= ah) & aj, bd <= 0 && (bd += this.DB, --bc)), 0 < ai && (ba = !0), ba && (bb += m(ai));
          }
          return ba ? bb : "0";
        }, b.prototype.negate = function ab() {
          var ag = w();
          return b.ZERO.subTo(this, ag), ag;
        }, b.prototype.abs = function ab() {
          return this.s < 0 ? this.negate() : this;
        }, b.prototype.compareTo = function ab(ac) {
          var ah = this.s - ac.s;
          if (0 != ah) return ah;
          var ai = this.t;
          if (0 != (ah = ai - ac.t)) return this.s < 0 ? -ah : ah;
          while (0 <= --ai) if (0 != (ah = this[ai] - ac[ai])) return ah;
          return 0;
        }, b.prototype.bitLength = function ab() {
          return this.t <= 0 ? 0 : this.DB * (this.t - 1) + y(this[this.t - 1] ^ this.s & this.DM);
        }, b.prototype.mod = function ab(ac) {
          var ah = w();
          return this.abs().divRemTo(ac, null, ah), this.s < 0 && 0 < ah.compareTo(b.ZERO) && ac.subTo(ah, ah), ah;
        }, b.prototype.modPowInt = function ab(ac, ad) {
          var ai;
          return ai = ac < 256 || ad.isEven() ? new bf(ad) : new be(ad), this.exp(ac, ai);
        }, b.ZERO = v(0), b.ONE = v(1), bg.prototype.doPublic = function ab(ac) {
          return ac.modPowInt(this.e, this.n);
        }, bg.prototype.setPublic = function ab(ac, ad) {
          null != ac && null != ad && 0 < ac.length && 0 < ad.length ? (this.n = function ab(ac, ad) {
            return new b(ac, ad);
          }(ac, 16), this.e = parseInt(ad, 16)) : console && console.error && console.error("Invalid RSA public key");
        }, bg.prototype.encrypt = function ab(ac) {
          var ah = function ab(ac, ad) {
            if (ad < ac.length + 11) return console && console.error && console.error("Message too long for RSA"), null;
            var ai = [],
              ba = ac.length - 1;
            while (0 <= ba && 0 < ad) {
              var i = ac.charCodeAt(ba--);
              i < 128 ? ai[--ad] = i : 127 < i && i < 2048 ? (ai[--ad] = 63 & i | 128, ai[--ad] = i >> 6 | 192) : (ai[--ad] = 63 & i | 128, ai[--ad] = i >> 6 & 63 | 128, ai[--ad] = i >> 12 | 224);
            }
            ai[--ad] = 0;
            var bb = new aj(),
              bc = [];
            while (2 < ad) {
              bc[0] = 0;
              while (0 == bc[0]) bb.nextBytes(bc);
              ai[--ad] = bc[0];
            }
            return ai[--ad] = 2, ai[--ad] = 0, new b(ai);
          }(ac, this.n.bitLength() + 7 >> 3);
          if (null == ah) return null;
          var s = this.doPublic(ah);
          if (null == s) return null;
          var n = s.toString(16);
          return 0 == (1 & n.length) ? n : "0" + n;
        }, bg;
      }();
      ac.default = ai;
    }
});
function arrayToHex(ac) {
    for (var t = [], s = 0, n = 0; n < 2 * ac.length; n += 2)
        t[n >>> 3] |= parseInt(ac[s], 10) << 24 - n % 8 * 4,
        s++;
    for (var i = [], r = 0; r < ac.length; r++) {
        var o = t[r >>> 2] >>> 24 - r % 4 * 8 & 255;
        i.push((o >>> 4).toString(16)),
        i.push((15 & o).toString(16));
    }
    return i.join("");
}

ba = loader(33);
bb = loader(34);
asymmetric = new bb.default();
symmetrical = ba.default;

function get_w(arg, random_str){
    // arg = '{"passtime":464,"userresponse":[[4467,5681]],"device_id":"","lot_number":"c010f9dea0f848378a9736970e032f8a","pow_msg":"1|0|md5|2025-07-15T21:28:18.249970+08:00|24f56dc13c40dc4a02fd0318567caef5|c010f9dea0f848378a9736970e032f8a||651350636a465caf","pow_sign":"61c5deb654acd115acc158bae1531856","geetest":"captcha","lang":"zh","ep":"123","biht":"1426265548","SPCP":"YTY2","36970e03":{"0e0032":"970e032f"},"em":{"ph":0,"cp":0,"ek":"11","wd":1,"nt":0,"si":0,"sc":0}}'
    _ = asymmetric.encrypt(random_str);
    u = symmetrical.encrypt(JSON.stringify(arg), random_str);
    w = arrayToHex(u) + _
    return w
}

// console.log(get_w({'passtime': 3391, 'userresponse': [[4521, 3081], [7524, 2733], [1683, 5019]], 'device_id': '', 'lot_number': '65fb8c8c1ccb4bc0bf849f43d66877ae', 'pow_msg': '1|12|sha1|2025-12-26T16:16:53.614003+08:00|b608ae7850d2e730b89b02a384d6b9cc|65fb8c8c1ccb4bc0bf849f43d66877ae||6e5c40bfb923a4ea', 'geetest': 'captcha', 'lang': 'zh', 'ep': '123', 'biht': '1426265548', 'LldF': '7rCZ', 'c1ccb4': {'5fb8d668': {'b8bf': 'bf84'}}, 'em': {'ph': 0, 'cp': 0, 'ek': '11', 'wd': 1, 'nt': 0, 'si': 0, 'sc': 0}, 'pow_sign': '0002437c1677c1a695e6ba98de165d64df06ea5a'}, '53ee12ccb0d32e00'))


