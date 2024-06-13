import os
import subprocess

msgpack_dir = r'D:\Workspaces\IDAWorkspace\evol_deepspace\lysk\assets\bundles_exported2\Assets\Build\Res\Battle\MessagePack'
out_dir = r'D:\Workspaces\IDAWorkspace\evol_deepspace\lysk\assets\bundles_exported2\Assets\Build\Res\Battle\MessagePack_dec'

def callX3Dec(f, typ=None):
    print('decode_x3', f)
    subprocess.check_call(['python3', 'x3msgpack_decode.py', f'{msgpack_dir}/{f}', f'{out_dir}/{f}.json', *([typ] if typ else [])])
    
def callDec(f, typ):
    print('decode', f)
    subprocess.check_call(['python3', 'msgpack_decode.py', f'{msgpack_dir}/{f}', f'{out_dir}/{f}.json', typ])

import glob

callX3Dec('AutoGen/BattleBossIntroduction.bytes', 'BattleBossIntroductions')

callX3Dec('AutoGen/BattleConsts.bytes')
callX3Dec('AutoGen/BattleFactionConfig.bytes', 'BattleFactionConfigs')
callX3Dec('AutoGen/BattleGuide.bytes', 'BattleGuides')
callX3Dec('AutoGen/BattleLevelConfig.bytes', 'BattleLevelConfigs')
callX3Dec('AutoGen/BattleManStrategy.bytes', 'BattleManStrategys')
callX3Dec('AutoGen/BattleSceneCameraCollider.bytes', 'BattleSceneCameraColliders')
callX3Dec('AutoGen/BattleSummon.bytes', 'BattleSummons')
callX3Dec('AutoGen/BattleTag.bytes', 'BattleTags')
callX3Dec('AutoGen/BattleWomanStrategy.bytes', 'BattleWomanStrategys')
callX3Dec('AutoGen/BuffLevelConfig.bytes', 'BuffLevelConfigs')
callX3Dec('AutoGen/BuffTagConflictConfig.bytes', 'BuffTagConflictConfigs')
callX3Dec('AutoGen/DialogueConfig.bytes', 'DialogueConfigs')
callX3Dec('AutoGen/DialogueKeyConfig.bytes', 'DialogueKeyConfigs')
callX3Dec('AutoGen/DialogueNameConfig.bytes', 'DialogueNameConfigs')
callX3Dec('AutoGen/EditorStageBaseCfg.bytes', 'EditorStageBaseCfgs')
callX3Dec('AutoGen/EditorStageCfg.bytes', 'EditorStageCfgs')
callX3Dec('AutoGen/EditorStageMonsterCfg.bytes', 'EditorStageMonsterCfgs')
callX3Dec('AutoGen/FemaleSuitConfig.bytes', 'FemaleSuitConfigs')
callX3Dec('AutoGen/FXConfig.bytes', 'FXConfigs')
callX3Dec('AutoGen/GroundMoveFx.bytes', 'GroundMoveFxs')
callX3Dec('AutoGen/HitParamConfig.bytes', 'HitParamConfigs')
callX3Dec('AutoGen/HurtMaterialConfig.bytes', 'HurtMaterialConfigs')
callX3Dec('AutoGen/HurtStateMapConfig.bytes', 'HurtStateMapConfigs')
callX3Dec('AutoGen/MaleSuitConfig.bytes', 'MaleSuitConfigs')
callX3Dec('AutoGen/MonsterBase.bytes', 'MonsterBases')
callX3Dec('AutoGen/MonsterProperty.bytes', 'MonsterPropertys')
# callX3Dec('AutoGen/OfflineHeroProperty.bytes') # ????
callX3Dec('AutoGen/PerformConfig.bytes', 'PerformConfigs')
callX3Dec('AutoGen/SkillPublicCdCfg.bytes', 'SkillPublicCdCfgs')
callX3Dec('AutoGen/StateToTimeline.bytes', 'StateToTimelines')
callX3Dec('AutoGen/WeaponLogicConfig.bytes', 'WeaponLogicConfigs')
callX3Dec('AutoGen/WeaponSkinConfig.bytes', 'WeaponSkinConfigs')

callDec('FxAnalyzer/FxCfg.bytes', 'FxCfg')
callX3Dec('Process/ActorCfg.bytes', 'ActorCfgs')
callDec('Process/SkillLevelCfg.bytes', 'SkillLevelCfgs')


for f in glob.glob('Buff/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'BuffCfg')

for f in glob.glob('DamageBox/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'DamageBoxCfg')


for f in glob.glob('Halo/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'HaloCfg')

for f in glob.glob('Item/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'ItemCfg')

for f in glob.glob('Level/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'StageConfig')

for f in glob.glob('MagicField/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'MagicFieldCfg')

for f in glob.glob('Missile/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'MissileCfg')

for f in glob.glob('ModelInfo/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'ModelInfo')

for f in glob.glob('Skill/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'SkillCfg')

for f in glob.glob('Skin/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'SkinCfg')

for f in glob.glob('Trigger/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'TriggerCfg')

for f in glob.glob('BattleLevelResAnalyzer/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'ResModule')
for f in glob.glob('HeroResAnalyzer/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'ResModule')
for f in glob.glob('SuitResAnalyzer/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'ResModule')
for f in glob.glob('WeaponResAnalyzer/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'ResModule')
    
for f in glob.glob(f'ActionModule/*.bytes', root_dir=msgpack_dir):
    callDec(f, 'ActionModuleCfg')