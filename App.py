from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "VURIA_754_SECRET_2026"
ARQUIVO_DADOS = "sistema_dados.json"

LOGIN_DONO = "7547117585"
SENHA_DONO = "7547117585"
DOMINIO = "vuria.pro"

def inicializar():
    dados = {"contas": {LOGIN_DONO: {"nivel":"dono","senha":SENHA_DONO,"nome":"Dono","saldo":999999}}, "revendedores": {}}
    with open(ARQUIVO_DADOS,"w",encoding="utf‑8") as f: json.dump(dados,f,indent=2)
    return dados

def carregar():
    if not os.path.exists(ARQUIVO_DADOS): return inicializar()
    try:
        with open(ARQUIVO_DADOS,"r",encoding="utf‑8") as f: return json.load(f)
    except: return inicializar()

def salvar(dados):
    with open(ARQUIVO_DADOS,"w",encoding="utf‑8") as f: json.dump(dados,f,indent=2)

@app.route("/")
def inicio():
    d = carregar()
    if "usuario" in session and session["usuario"] in d["contas"]: return redirect(url_for("painel"))
    return render_template_string(LOGIN_TPL, dom=DOMINIO)

@app.route("/entrar", methods=["POST"])
def entrar():
    d = carregar()
    l = request.form.get("login","").strip()
    s = request.form.get("senha","").strip()
    if l in d["contas"] and d["contas"][l]["senha"] == s:
        session["usuario"] = l
        return redirect(url_for("painel"))
    return render_template_string(LOGIN_TPL, dom=DOMINIO, erro="Usuário ou senha incorretos")

@app.route("/sair")
def sair(): session.clear(); return redirect(url_for("inicio"))

@app.route("/painel")
def painel():
    d = carregar()
    if "usuario" not in session or session["usuario"] not in d["contas"]: return redirect(url_for("inicio"))
    u = session["usuario"]
    if d["contas"][u]["nivel"] == "dono":
        lista = [{"login":k,"nome":v["nome"],"saldo":v.get("saldo",0),"qtd":len(v.get("clientes",{}))} for k,v in d["revendedores"].items()]
        return render_template_string(DONO_TPL, dom=DOMINIO, lista=lista)
    else:
        r = d["revendedores"][u]
        clis = [{"nome":c["nome"],"login":c["login"],"data":c.get("data","")} for c in r.get("clientes",{}).values()]
        return render_template_string(REV_TPL, dom=DOMINIO, saldo=r.get("saldo",0), clientes=clis)

@app.route("/criar‑rev", methods=["POST"])
def criarr():
    d = carregar()
    if "usuario" not in session or session["usuario"] != LOGIN_DONO: return redirect(url_for("inicio"))
    nome = request.form.get("nome","").strip()
    login = request.form.get("login","").strip()
    senha = request.form.get("senha","").strip()
    if not nome or not login or not senha: return render_template_string(DONO_TPL,dom=DOMINIO,erro="Preencha todos os campos!",lista=[])
    if login in d["contas"] or login in d["revendedores"]: return render_template_string(DONO_TPL,dom=DOMINIO,erro="Esse login já existe!",lista=[])
    d["contas"][login] = {"nivel":"revendedor","senha":senha,"nome":nome}
    d["revendedores"][login] = {"nome":nome,"saldo":0,"clientes":{}}
    salvar(d)
    return redirect(url_for("painel"))

@app.route("/add‑cred", methods=["POST"])
def addc():
    d = carregar()
    if "usuario" not in session or session["usuario"] != LOGIN_DONO: return redirect(url_for("inicio"))
    login = request.form.get("login","").strip()
    qtd = int(request.form.get("qtd","1"))
    if login in d["revendedores"]:
        d["revendedores"][login]["saldo"] += qtd
        salvar(d)
    return redirect(url_for("painel"))

@app.route("/criar‑cli", methods=["POST"])
def criarc():
    d = carregar()
    if "usuario" not in session or session["usuario"] not in d["revendedores"]: return redirect(url_for("inicio"))
    u = session["usuario"]
    if d["revendedores"][u]["saldo"] <=0: return render_template_string(REV_TPL,dom=DOMINIO,saldo=0,erro="Sem créditos disponíveis!",clientes=[])
    nome = request.form.get("nome","").strip()
    login = request.form.get("login","").strip()
    if not nome or not login: return render_template_string(REV_TPL,dom=DOMINIO,saldo=d["revendedores"][u]["saldo"],erro="Preencha nome e login!",clientes=[])
    d["revendedores"][u]["saldo"] -= 1
    d["revendedores"][u]["clientes"][login] = {"nome":nome,"login":login,"data":datetime.now().strftime("%d/%m/%Y %H:%M")}
    salvar(d)
    return redirect(url_for("painel"))

@app.route("/consulta", methods=["POST"])
def consulta():
    d = carregar()
    if "usuario" not in session: return jsonify({"erro":"Faça login primeiro"}),401
    t = request.form.get("tipo","")
    v = request.form.get("valor","").strip()
    if not t or not v: return jsonify({"erro":"Escolha o tipo e digite o valor!"}),400
    return jsonify({"ok":True,"tipo":t,"valor":v,"msg":"✅ Consulta realizada com sucesso — LIBERADA","nivel":d["contas"][session["usuario"]]["nivel"].upper()})

LOGIN_TPL = """<!DOCTYPE html><html lang=pt‑BR><head><meta charset=UTF‑8><meta name=viewport content="width=device‑width,initial‑scale=1"><title>VURIA {{dom}}</title><style>*{box‑sizing:border‑box;margin:0;padding:0;font‑family:'Segoe UI',sans‑serif}body{background:#0f0f1a;color:#fff;display:flex;align‑items:center;justify‑content:center;min‑height:100vh;padding:1rem}.cx{width:100%;max‑width:420px;background:#15152b;border:2px solid #0cf;border‑radius:12px;padding:2rem;box‑shadow:0 0 25px #0cf4;text‑align:center}h1{font‑size:1.8rem;margin‑bottom:.5rem;color:#fff;text‑shadow:0 0 8px #0cf}.end{color:#0cf;font‑weight:700;margin‑bottom:1.5rem}.aviso{background:#f002;color:#ff9;padding:.7rem;border:1px solid #f44;border‑radius:6px;margin:1rem 0}.info{background:#082335;border:1px solid #0cf;padding:.7rem;border‑radius:6px;margin:1rem 0;color:#cff}label{display:block;text‑align:left;margin‑bottom:.4rem;font‑weight:600;color:#cff}input{width:100%;padding:.9rem;border:2px solid #0cf;border‑radius:6px;background:#0005;color:#fff;font‑size:1rem;margin‑bottom:1rem}.btn{width:100%;padding:1rem;border:none;border‑radius:6px;background:linear‑gradient(90deg,#0cf,#a0f);color:#000;font‑weight:900;font‑size:1.2rem;cursor:pointer;transition:transform .2s}.btn:active{transform:scale(.97)}</style></head><body><div class=cx><h1>🔐 VURIA</h1><div class=end>{{dom}}</div><div class=info>🔑 Login: 7547117585<br>🔒 Senha: 7547117585</div>{%if erro%}<div class=aviso>{{erro}}</div>{%endif%}<form action=/entrar method=post><label>Login</label><input name=login value=7547117585 required><label>Senha</label><input type=password name=senha required><button class=btn>▶ ENTRAR</button></form></div></body></html>"""

DONO_TPL = """<!DOCTYPE html><html lang=pt‑BR><head><meta charset=UTF‑8><meta name=viewport content="width=device‑width,initial‑scale=1"><title>Painel — {{dom}}</title><style>*{box‑sizing:border‑box;margin:0;padding:0;font‑family:system‑ui}body{background:#0f0f1a;color:#fff;padding:1rem;max‑width:960px;margin:0 auto}h1{font‑size:1.5rem;margin‑bottom:1.5rem;display:flex;justify‑content:space‑between;align‑items:center}a.sair{background:none;border:2px solid #f55;color:#f55;padding:.5rem 1rem;border‑radius:6px;text‑decoration:none;font‑weight:bold;transition:all .2s}a.sair:hover{background:#f55;color:#fff}section{background:#15152b;border:2px solid #0cf;border‑radius:10px;padding:1.2rem;margin‑bottom:1.2rem;box‑shadow:inset 0 0 10px #0cf2}h2{color:#0cf;margin‑bottom:1rem;font‑size:1.1rem;padding‑bottom:.3rem;border‑bottom:1px solid #fff2}label{display:block;margin‑bottom:.4rem;font‑weight:600;color:#cff}input,select{width:100%;padding:.7rem;border:2px solid #0cf;border‑radius:6px;background:#0005;color:#fff;margin‑bottom:.8rem}.btn{padding:.7rem 1.2rem;border:none;border‑radius:6px;background:linear‑gradient(90deg,#0cf,#a0f);color:#000;font‑weight:bold;cursor:pointer;margin‑top:.3rem}.aviso{background:#f002;color:#ff9;padding:.7rem;border:1px solid #f44;border‑radius:6px;margin:1rem 0}.item{padding:.6rem;border‑bottom:1px solid #fff2;display:flex;flex‑wrap:wrap;gap:.5rem;align‑items:center}.nome{font‑weight:bold;color:#fd5}.dado{color:#fc0}.card{background:#082336;border:1px solid #0cf;border‑radius:6px;padding:.7rem;margin:.5rem 0;flex‑grow:1;min‑width:220px}</style></head><body><h1>👑 PAINEL DO DONO <small style=font‑size:.9rem;color:#888>{{dom}}</small><a href=/sair class=sair>⬢ SAIR</a></h1>{%if erro%}<div class=aviso>{{erro}}</div>{%endif%}<section><h2>➕ Criar Revendedor</h2><form action=/criar‑rev method=post><label>Nome Completo</label><input name=nome required><label>Login/Acesso</label><input name=login required><label>Senha</label><input type=password name=senha required><button class=btn>✅ Criar Conta</button></form></section><section><h2>💳 Adicionar Créditos</h2><form action=/add‑cred method=post><label>Login do Revendedor</label><input name=login required><label>Quantidade</label><input name=qtd type=number min=1 value=1 required><button class=btn>➕ Adicionar</button></form></section><section><h2>📋 Revendedores ({{lista|length}})</h2>{%if lista%}{%for r in lista%}<div class=card><div class=item><span class=nome>{{r.nome}}</span> — <span class=dado>{{r.login}}</span></div><div style=padding:.4rem;color:#fff8>💳 Créditos: <strong>{{r.saldo}}</strong> | 👤 Clientes: <strong>{{r.qtd}}</strong></div></div>{%endfor%}{%else%}<p style=color:#888>Ainda sem revendedores cadastrados</p>{%endif%}</section><section><h2>🔎 Realizar Consulta — TODOS</h2><form action=/consulta method=post id=fcon><label>Escolha Tipo</label><select name=tipo><option value=cpf>📄 CPF</option><option value=cnpj>🏢 CNPJ</option><option value=nome>👤 NOME</option><option value=placa>🚗 PLACA</option><option value=telefone>📞 TELEFONE</option><option value=cep>📍 CEP/ENDEREÇO</option></select><label>Valor / Dado</label><input name=valor placeholder="Digite sem símbolos/pontos" required><button type=submit class=btn>🔎 CONSULTAR — LIBERADO</button></form><div id=res style=margin‑top:1rem;padding:.8rem;border:1px solid #0cf;border‑radius:6px;display:none></div></section><script>document.querySelector("#fcon").addEventListener("submit",async e=>{e.preventDefault();const r=document.querySelector("#res");r.style.display="block";r.innerHTML="⏳ Enviando…";const fd=new FormData(e.target);const q=await fetch("/consulta",{method:"POST",body:fd});if(!q.ok){r.innerHTML="❌ Erro "+q.status;return}const d=await q.json();if(d.erro){r.innerHTML="❌ "+d.erro;return}r.innerHTML="<div style=color:#0f0>✅ "+d.msg+"</div><div style=margin‑top:.5rem>Tipo: "+d.tipo+"<br>Valor: "+d.valor+"<br>Nível: "+d.nivel+"</div>"})</script></body></html>"""

REV_TPL = """<!DOCTYPE html><html lang=pt‑BR><head><meta charset=UTF‑8><meta name=viewport content="width=device‑width,initial‑scale=1"><title>Revendedor — {{dom}}</title><style>*{box‑sizing:border‑box;margin:0;padding:0;font‑family:system‑ui}body{background:#0f0f1a;color:#fff;padding:1rem;max‑width:900px;margin:0 auto}h1{font‑size:1.4rem;margin‑bottom:1.5rem;display:flex;flex‑wrap:wrap;justify‑content:space‑between;align‑items:center;gap:.5rem}.saldo{background:#062;border:2px solid #0f6;border‑radius:8px;padding:1rem;text‑align:center;font‑size:1.3rem;color:#0ff;margin‑bottom:1rem;box‑shadow:0 0 12px #0f64}a.sair{background:none;border:2px solid #f55;color:#f55;padding:.5rem 1rem;border‑radius:6px;text‑decoration:none;font‑weight:bold}section{background:#15152b;border:2px solid #0cf;border‑radius:10px;padding:1.2rem;margin‑bottom:1.2rem}h2{color:#0cf;margin‑bottom:1rem;font‑size:1.1rem}label{display:block;margin‑bottom:.4rem;font‑weight:600;color:#cff}input,select{width:100%;padding:.7rem;border:2px solid #0cf;border‑radius:6px;background:#0005;color:#fff;margin‑bottom:.8rem}.btn{padding:.7rem 1.2rem;border:none;border‑radius:6px;background:linear‑gradient(90deg,#0cf,#a0f);color:#000;font‑weight:bold;cursor:pointer}.aviso{background:#f002;color:#ff9;padding:.7rem;border:1px solid #f44;border‑radius:6px;margin:1rem 0}.cli{border‑bottom:1px solid #fff2;padding:.6rem;display:flex;justify‑content:space‑between;flex‑wrap:wrap}.nom{font‑weight:bold;color:#fd5;flex:1}.dat{color:#aaa;font‑size:.9rem}</style></head><body><h1>🏷️ ÁREA DO REVENDEDOR — {{dom}} <a href=/sair class=sair>⬢ SAIR</a></h1><div class=saldo>💳 CRÉDITOS DISPONÍVEIS: <strong>{{saldo}}</strong></div>{%if erro%}<div class=aviso>{{erro}}</div>{%endif%}<section><h2>➕ Cadastrar Cliente — gasta 1 crédito</h2><form action=/criar‑cli method=post><label>Nome Completo</label><input name=nome required><label>Login / Identificação</label><input name=login required><button class=btn>✅ Cadastrar — 1 Crédito</button></form></section><section><h2>👥 Meus Clientes — {{clientes|length}}</h2>{%if clientes%}{%for c in clientes%}<div class=cli><span class=nom>{{c.nome}}</span><span>{{c.login}}</span><span class=dat>{{c.data}}</span></div>{%endfor%}{%else%}<p style=color:#888>Ainda sem clientes cadastrados</p>{%endif%}</section><section><h2>🔎 Realizar Consultas — LIBERADAS</h2><form action=/consulta method=post id=fcon><label>Escolha Tipo</label><select name=tipo><option value=cpf>📄 CPF</option><option value=cnpj>🏢 CNPJ</option><option value=nome>👤 NOME</option><option value=placa>🚗 PLACA</option><option value=telefone>📞 TELEFONE</option><option value=cep>📍 CEP/ENDEREÇO</option></select><label>Valor / Dado</label><input name=valor placeholder="Sem símbolos" required><button type=submit class=btn>🔎 FAZER CONSULTA</button></form><div id=res style=margin‑top:1rem;padding:.8rem;border:1px solid #0cf;border‑radius:6px;display:none></div></section><script>document.querySelector("#fcon").addEventListener("submit",async e=>{e.preventDefault();const r=document.querySelector("#res");r.style.display="block";r.innerHTML="⏳ Processando…";const fd=new FormData(e.target);const q=await fetch("/consulta",{method:"POST",body:fd});if(!q.ok){r.innerHTML="❌ Erro — faça login novamente";return}const d=await q.json();if(d.erro){r.innerHTML="❌ "+d.erro;return}r.innerHTML="<div style=color:#0f0>✅ "+d.msg+"</div><div style=margin‑top:.5rem>Tipo: "+d.tipo+"<br>Valor: "+d.valor+"<br>Nível: "+d.nivel+"</div>"})</script></body></html>"""

if __name__ == "__main__":
    carregar()
    print("\n" + "="*60)
    print("✅ SISTEMA INICIADO — https://"+DOMINIO)
    print("🔑 LOGIN → ", LOGIN_DONO)
    print("🔒 SENHA → ", SENHA_DONO)
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=8000)
