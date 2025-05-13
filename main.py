from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

players = {}
last_turn = None  # Username of last player who made a move
total_players = []  # Order-preserved list of joined users


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào mừng đến với bot Bi-a tính điểm! Dùng /join để tham gia trò chơi."
    )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.username or update.message.from_user.first_name
    if user not in players:
        players[user] = 0
        total_players.append(user)
        await update.message.reply_text(f"{user} đã tham gia trò chơi.")
    else:
        await update.message.reply_text(f"{user} đã tham gia từ trước.")


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not players:
        await update.message.reply_text("Chưa có người chơi nào.")
        return
    msg = "\u2728 Bảng điểm hiện tại:\n"
    for user, pts in players.items():
        msg += f"{user}: {pts} điểm\n"
    await update.message.reply_text(msg)


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_turn
    user = update.message.from_user.username or update.message.from_user.first_name
    if user not in players:
        await update.message.reply_text(
            "Bạn chưa tham gia game. Dùng /join trước.")
        return
    try:
        cards = int(context.args[0])
    except:
        await update.message.reply_text("Dùng cú pháp: /end <số_bài>")
        return

    context.chat_data.setdefault('round_data', {})[user] = cards
    await update.message.reply_text(f"{user} còn {cards} lá bài.")

    # Check if all players submitted
    if len(context.chat_data['round_data']) < len(players):
        return

    # Tính điểm
    data = context.chat_data['round_data']
    min_cards = min(data.values())
    winners = [u for u, c in data.items() if c == min_cards]

    if len(winners) > 1:
        await update.message.reply_text(
            "Có nhiều người thắng, không tính điểm.")
    else:
        winner = winners[0]
        total_gain = 0
        for u, c in data.items():
            if u != winner:
                players[u] -= c
                total_gain += c
        players[winner] += total_gain
        await update.message.reply_text(
            f"{winner} thắng ván này và nhận {total_gain} điểm!")

    last_turn = None
    context.chat_data['round_data'] = {}


async def hole10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_turn
    user = update.message.from_user.username or update.message.from_user.first_name
    if user not in players:
        await update.message.reply_text(
            "Bạn chưa tham gia game. Dùng /join trước.")
        return
    try:
        X = int(context.args[0])
    except:
        await update.message.reply_text(
            "Dùng cú pháp: /10 <số bi> [@username nếu là Bi Đền]")
        return

    is_bi_denden = len(context.args) >= 2
    if is_bi_denden:
        offender = context.args[1].lstrip('@')
        if offender not in players:
            await update.message.reply_text(
                "Người bị đền không tồn tại trong trò chơi.")
            return
        N = len(players)
        penalty = X * (2 if N == 2 else (N - 1))
        players[offender] -= penalty
        players[user] += penalty
        await update.message.reply_text(
            f"Bi Đền! {offender} mất {penalty} điểm, {user} nhận được.")
    else:
        gain = X * (len(players) - 1)
        for u in players:
            if u != user:
                players[u] -= X
        players[user] += gain
        await update.message.reply_text(
            f"{user} ăn {X} bi ở lỗ 10 và nhận {gain} điểm từ những người chơi khác."
        )

    last_turn = user


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    players.clear()
    total_players.clear()
    context.chat_data.clear()
    await update.message.reply_text(
        "Game đã được đặt lại. Tất cả người chơi đã thoát.")


app = ApplicationBuilder().token(
    "7519846312:AAFFodb0zVpjAPPLGygeOE232UBdEYTh7B4").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("join", join))
app.add_handler(CommandHandler("score", score))
app.add_handler(CommandHandler("end", end))
app.add_handler(CommandHandler("10", hole10))
app.add_handler(CommandHandler("reset", reset))

app.run_polling()

